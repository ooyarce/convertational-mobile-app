import asyncio
import json
import logging

from google import genai
from google.genai import types

from app.config import settings
from app.core.prompts import SYSTEM_PROMPT
from app.core.tools import property_tools
from app.schemas.conversation import ChatRequest, ChatResponse, Message, Role
from app.services.properties import convert_currency, properties_client

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10
MAX_RETRIES = 3
RETRY_BASE_DELAY = 15  # seconds

# Map tool names to service methods
TOOL_DISPATCH = {
    "search_locations": properties_client.search_locations,
    "list_properties": properties_client.list_properties,
    "get_property_detail": properties_client.get_property_detail,
    "convert_currency": convert_currency,
}


def _build_contents(history: list[Message], user_message: str) -> list[types.Content]:
    """Convert chat history + new message into Gemini-format contents."""
    contents: list[types.Content] = []

    for msg in history:
        role = "user" if msg.role == Role.USER else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=msg.content)],
        ))

    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)],
    ))
    return contents


def _coerce_args(name: str, args: dict) -> dict:
    """Fix type mismatches from LLMs that send strings instead of numbers."""
    int_fields = {"bedrooms_min", "bathrooms_min", "parkplaces_min"}
    float_fields = {"price_max", "build_size_min", "lot_size_min", "amount"}
    for k, v in args.items():
        if k in int_fields and isinstance(v, str):
            args[k] = int(v)
        elif k in float_fields and isinstance(v, str):
            args[k] = float(v)
    return args


async def _execute_tool_call(name: str, arguments: dict) -> str:
    """Execute a single tool call and return the result as string."""
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool '{name}'"})

    try:
        args = _coerce_args(name, dict(arguments))
        logger.info("Calling tool %s with args: %s", name, args)
        result = await fn(**args)
        return result
    except Exception as e:
        logger.error("Tool %s failed: %s", name, str(e))
        return json.dumps({"error": f"Error calling {name}: {str(e)}"})


async def _generate_with_retry(client: genai.Client, **kwargs) -> object:
    """Call Gemini with manual exponential backoff on transient errors (429, 503, 500).

    Daily quota exhaustion (PerDay) is NOT retried — it fails immediately.
    """
    RETRYABLE = ("429", "503", "500", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "INTERNAL")

    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.models.generate_content(**kwargs)
        except Exception as e:
            error_str = str(e)

            # Daily quota — no point retrying, fail fast
            if "PerDay" in error_str:
                logger.error("Daily quota exhausted — not retrying: %s", error_str[:200])
                raise

            is_transient = any(code in error_str for code in RETRYABLE)

            if is_transient and attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning(
                    "Transient error (%s), retrying in %ds (attempt %d/%d)",
                    error_str[:80], delay, attempt + 1, MAX_RETRIES,
                )
                await asyncio.sleep(delay)
            else:
                logger.error("Gemini call failed after %d attempts: %s", attempt + 1, error_str[:200])
                raise

    raise last_error


async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request through Gemini with function calling."""
    # Disable SDK built-in tenacity retry — we handle retries manually
    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    contents = _build_contents(request.history, request.message)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=property_tools,
        temperature=0.7,
        max_output_tokens=2048,
    )

    for _ in range(MAX_TOOL_ITERATIONS):
        response = await _generate_with_retry(
            client,
            model=settings.llm_model,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        parts = (candidate.content and candidate.content.parts) or []

        logger.info(
            "Response: finish_reason=%s, parts=%d",
            candidate.finish_reason,
            len(parts),
        )
        for i, part in enumerate(parts):
            if part.function_call:
                logger.info("  Part[%d]: function_call=%s", i, part.function_call.name)
            elif part.text:
                logger.info("  Part[%d]: text (%d chars, thought=%s)", i, len(part.text), getattr(part, "thought", False))
            else:
                logger.info("  Part[%d]: other=%s", i, type(part))

        # Collect function calls from response parts
        function_calls = [
            part.function_call
            for part in parts
            if part.function_call is not None
        ]

        # If no function calls, we have the final text answer
        if not function_calls:
            # Extract text directly from parts — response.text can raise
            # ValueError when the response contains thought/thinking parts
            # (common with gemini-2.5 models)
            text_pieces = []
            for part in parts:
                if part.text and not getattr(part, "thought", False):
                    text_pieces.append(part.text)
            final_text = "".join(text_pieces).strip()

            if not final_text:
                # Fallback: try response.text
                try:
                    final_text = response.text or ""
                except (AttributeError, ValueError):
                    pass

            logger.info("Final response length: %d chars", len(final_text))
            return ChatResponse(
                content=final_text or "Lo siento, no pude generar una respuesta."
            )

        # Append model response (with function call parts) to contents
        contents.append(candidate.content)

        # Execute each function call and build response parts
        function_response_parts: list[types.Part] = []
        for fc in function_calls:
            result_str = await _execute_tool_call(fc.name, fc.args)
            logger.info("Tool %s completed", fc.name)

            # Parse result to dict for Gemini (it expects a dict, not a string)
            try:
                result_data = json.loads(result_str)
            except (json.JSONDecodeError, TypeError):
                result_data = {"result": result_str}

            function_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response=result_data,
                )
            )

        # Append all function responses as a single user turn
        contents.append(types.Content(
            role="user",
            parts=function_response_parts,
        ))

    return ChatResponse(
        content="Lo siento, no pude completar la búsqueda. Por favor intenta de nuevo."
    )
