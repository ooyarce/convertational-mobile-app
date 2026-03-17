"""Benchmark: Gemini vs Groq — PropAssist AI Function Calling.

Properly handles free tier rate limits:
  - Gemini: 15 RPM → 20s delay between tests
  - Groq:   60 RPM → 2s delay between tests

Usage:  python benchmark.py
"""

import asyncio
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types as gtypes
from groq import Groq

from app.config import settings
from app.core.prompts import SYSTEM_PROMPT
from app.core.tools import property_tools as groq_tools
from app.services.properties import properties_client

# ── Models ───────────────────────────────────────────────────────────────────

MODELS = [
    {"name": "qwen/qwen3-32b", "provider": "groq", "delay": 3},
    {"name": "gemini-3.1-flash-lite-preview", "provider": "gemini", "delay": 25},
]

TEST_CASES = [
    {
        "id": "greeting",
        "name": "Saludo simple",
        "message": "Hola, buenas tardes",
        "expect_tools": False,
        "check_keywords": ["hola", "ayudar", "propiedad", "busca", "buenas"],
    },
    {
        "id": "search",
        "name": "Busqueda con function calling",
        "message": "Busco un departamento de 2 dormitorios en Las Condes, hasta 5.000 UF",
        "expect_tools": True,
        "check_keywords": ["las condes", "departamento", "uf", "dormitorio", "propiedad"],
    },
    {
        "id": "offtopic",
        "name": "Off-topic rechazado",
        "message": "Cual es la capital de Francia?",
        "expect_tools": False,
        "check_keywords": ["inmobiliario", "propiedad", "solo", "ayudar", "busca"],
    },
]

# ── Shared ───────────────────────────────────────────────────────────────────

TOOL_DISPATCH = {
    "search_locations": properties_client.search_locations,
    "list_properties": properties_client.list_properties,
    "get_property_detail": properties_client.get_property_detail,
}


async def exec_tool(name, args):
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return f"Unknown tool: {name}"
    for k in ("bedrooms_min",):
        if k in args and isinstance(args[k], str):
            args[k] = int(args[k])
    for k in ("price_max",):
        if k in args and isinstance(args[k], str):
            args[k] = float(args[k])
    return await fn(**args)


# ── Groq runner ──────────────────────────────────────────────────────────────

async def run_groq(model, message):
    client = Groq(api_key=settings.groq_api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    tools_used = []
    api_calls = 0
    start = time.perf_counter()

    try:
        for _ in range(10):
            api_calls += 1
            resp = client.chat.completions.create(
                model=model, messages=messages, tools=groq_tools,
                temperature=0.7, max_tokens=2048,
            )
            choice = resp.choices[0]
            if not choice.message.tool_calls:
                break

            assistant_msg = {
                "role": "assistant", "content": choice.message.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in choice.message.tool_calls
                ],
            }
            messages.append(assistant_msg)
            for tc in choice.message.tool_calls:
                tools_used.append(tc.function.name)
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                result = await exec_tool(tc.function.name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        return {
            "ok": True, "time": round(time.perf_counter() - start, 2),
            "tools": tools_used, "api_calls": api_calls,
            "text": choice.message.content or "",
        }
    except Exception as e:
        return {"ok": False, "time": round(time.perf_counter() - start, 2),
                "tools": tools_used, "api_calls": api_calls, "text": "", "error": str(e)[:150]}


# ── Gemini runner ────────────────────────────────────────────────────────────

gemini_tool_decls = []
for t in groq_tools:
    gemini_tool_decls.append(gtypes.FunctionDeclaration(
        name=t["function"]["name"],
        description=t["function"]["description"],
        parameters_json_schema=t["function"]["parameters"],
    ))
gemini_tools_obj = gtypes.Tool(function_declarations=gemini_tool_decls)


async def run_gemini(model, message):
    client = genai.Client(api_key=settings.gemini_api_key)
    config = gtypes.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT, tools=[gemini_tools_obj],
        temperature=0.7, max_output_tokens=2048,
    )
    contents = [gtypes.Content(role="user", parts=[gtypes.Part(text=message)])]
    tools_used = []
    api_calls = 0
    start = time.perf_counter()

    try:
        for _ in range(10):
            api_calls += 1
            resp = client.models.generate_content(model=model, contents=contents, config=config)
            candidate = resp.candidates[0]
            contents.append(candidate.content)
            fcs = [p.function_call for p in candidate.content.parts if p.function_call]
            if not fcs:
                break
            parts = []
            for fc in fcs:
                tools_used.append(fc.name)
                args = dict(fc.args) if fc.args else {}
                result = await exec_tool(fc.name, args)
                parts.append(gtypes.Part.from_function_response(name=fc.name, response={"output": result}))
            contents.append(gtypes.Content(role="tool", parts=parts))

        return {
            "ok": True, "time": round(time.perf_counter() - start, 2),
            "tools": tools_used, "api_calls": api_calls,
            "text": resp.text or "",
        }
    except Exception as e:
        return {"ok": False, "time": round(time.perf_counter() - start, 2),
                "tools": tools_used, "api_calls": api_calls, "text": "", "error": str(e)[:150]}


# ── Main ─────────────────────────────────────────────────────────────────────

RUNNERS = {"groq": run_groq, "gemini": run_gemini}


async def main():
    print("=" * 90)
    print("  BENCHMARK: PropAssist AI - Function Calling (Free Tier)")
    print("=" * 90)
    print(f"  Modelos: {len(MODELS)}")
    print(f"  Tests:   {len(TEST_CASES)}")
    print(f"  Nota:    Delays entre tests respetan RPM de cada proveedor")
    print("=" * 90)

    all_results = {}

    for m in MODELS:
        model = m["name"]
        provider = m["provider"]
        delay = m["delay"]
        runner = RUNNERS[provider]
        all_results[model] = {"provider": provider, "tests": []}

        print(f"\n  >> {model} ({provider}, delay={delay}s)")

        for i, test in enumerate(TEST_CASES):
            if i > 0:
                print(f"     ... esperando {delay}s (rate limit) ...", flush=True)
                await asyncio.sleep(delay)

            print(f"     [{i+1}/{len(TEST_CASES)}] {test['name']} ... ", end="", flush=True)
            result = await runner(model, test["message"])

            if result["ok"]:
                has_keywords = any(w in result["text"].lower() for w in test["check_keywords"])
                used_tools = bool(result["tools"])
                correct_tool_usage = (test["expect_tools"] == used_tools)

                status = "PASS" if has_keywords else "WEAK"
                tool_str = ", ".join(result["tools"]) if result["tools"] else "none"
                tool_ok = "correct" if correct_tool_usage else "WRONG"

                print(f'{result["time"]}s | {result["api_calls"]} API calls | tools=[{tool_str}] ({tool_ok}) | {status}')
                print(f"              Response: {result['text'][:120]}...")

                result["status"] = status
                result["correct_tools"] = correct_tool_usage
            else:
                print(f'ERROR | {result.get("error", "")}')
                result["status"] = "ERROR"
                result["correct_tools"] = False

            result["test_id"] = test["id"]
            all_results[model]["tests"].append(result)

    # ── Summary table ────────────────────────────────────────────────────────
    print(f"\n{'=' * 90}")
    print("  TABLA RESUMEN")
    print(f"{'=' * 90}")
    print(f"  {'Modelo':<48} {'Saludo':>10} {'FC':>10} {'OffTop':>10} {'Total':>8}")
    print(f"  {'─' * 86}")

    ranking = []

    for model, data in all_results.items():
        cols = []
        total_score = 0
        total_time = 0
        ok_count = 0

        for t in data["tests"]:
            if t["status"] == "ERROR":
                cols.append("ERR")
            else:
                cols.append(f'{t["time"]}s')
                total_time += t["time"]
                ok_count += 1
                if t["status"] == "PASS":
                    total_score += 1
                if t["correct_tools"]:
                    total_score += 1

        avg = round(total_time / ok_count, 2) if ok_count else -1
        short = model if len(model) <= 46 else "..." + model[-43:]

        while len(cols) < 3:
            cols.append("N/A")
        print(f"  {short:<48} {cols[0]:>10} {cols[1]:>10} {cols[2]:>10} {total_score:>6}/6")
        ranking.append((model, data["provider"], total_score, avg, ok_count))

    # ── Final ranking ────────────────────────────────────────────────────────
    ranking.sort(key=lambda x: (-x[2], x[3] if x[3] > 0 else 999))

    print(f"\n{'=' * 90}")
    print("  RANKING FINAL (score + velocidad)")
    print(f"{'=' * 90}")
    for i, (model, provider, score, avg, ok) in enumerate(ranking):
        pos = f"  {i+1}."
        avg_str = f"{avg}s" if avg > 0 else "N/A"
        tests_str = f"{ok}/3 tests OK"
        print(f"{pos} [{provider:>6}] {model:<48} {score}/6 pts  avg={avg_str}  ({tests_str})")

    w = ranking[0]
    print(f"\n  GANADOR: {w[0]} ({w[1]})")
    print(f"  Score: {w[2]}/6 | Tiempo promedio: {w[3]}s | Tests exitosos: {w[4]}/3")
    print(f"{'=' * 90}\n")


if __name__ == "__main__":
    asyncio.run(main())
