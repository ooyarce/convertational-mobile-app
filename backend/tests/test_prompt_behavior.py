"""Tests for LLM conversational behavior — validates prompt engineering.

These tests hit the real Gemini API. Each test has a delay to respect rate limits.
Run with:  pytest tests/test_prompt_behavior.py -v

NOTE: LLM responses are non-deterministic. These tests check broad behavioral
patterns (e.g. "does the response mention real estate?"), not exact wording.
"""
import asyncio

import pytest

from app.core.agent import chat
from app.schemas.conversation import ChatRequest, Message, Role

_DELAY = 20  # seconds between tests to respect RPM


def _contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(kw in text for kw in keywords)


@pytest.mark.asyncio
class TestConversationalBehavior:
    """Core conversational behaviors that the prompt must enforce."""

    async def test_no_redundant_introduction(self):
        """When the bot already introduced itself, a new greeting should NOT
        repeat the full introduction (name + role)."""
        history = [
            Message(role=Role.USER, content="Hola"),
            Message(role=Role.ASSISTANT, content=(
                "¡Hola! Soy PropAssist AI, tu asistente inmobiliario. "
                "¿Buscas comprar o arrendar? ¿Tienes alguna zona en mente?"
            )),
        ]
        request = ChatRequest(message="Hola de nuevo", history=history)
        response = await chat(request)
        # Should NOT re-introduce itself with "Soy PropAssist"
        assert "soy propassist" not in response.content.lower()

    async def test_vague_input_asks_clarification(self):
        """Vague requests should trigger clarifying questions about
        operation, type, or budget — not a blind search."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(message="Busco algo en Santiago")
        response = await chat(request)
        # Should ask about at least one of: buy/rent, property type, budget
        assert _contains_any(response.content, [
            "arriendo", "arrendar", "venta", "compra", "comprar",
            "departamento", "casa", "tipo", "presupuesto", "dormitorio",
        ])

    async def test_offensive_text_apologizes(self):
        """Offensive input should get a brief apology and redirect."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(message="Eres un idiota inútil")
        response = await chat(request)
        assert _contains_any(response.content, [
            "lamento", "disculpa", "perdón", "ayud", "propiedad",
        ])

    async def test_off_topic_redirects_to_realestate(self):
        """Non real-estate questions should be declined and redirected."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(message="¿Cuántos planetas tiene el sistema solar?")
        response = await chat(request)
        assert _contains_any(response.content, [
            "propiedad", "inmobili", "especialidad", "ayud", "busca",
        ])

    async def test_clp_search_converts_and_finds(self):
        """When user mentions CLP price, the agent should convert to UF
        and search properties (using convert_currency tool)."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(
            message="Busco un departamento en Las Condes de arriendo, menos de 2 millones de pesos"
        )
        response = await chat(request)
        # Should have attempted a property search (found results or reported none)
        assert _contains_any(response.content, [
            "las condes", "departamento", "encontr", "propiedad",
            "resultado", "opcio", "disponible", "uf", "pesos", "arriendo",
        ])
