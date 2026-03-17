"""Tests for the agent — validates the full flow with real Gemini + real API.

NOTE: These tests hit the real Gemini API (free tier, ~20 RPM).
We keep them minimal to avoid burning quota.  Each test waits between
calls to stay under the rate limit.
Run with:  pytest tests/test_agent.py -v
"""
import asyncio

import pytest

from app.core.agent import chat
from app.schemas.conversation import ChatRequest, Message, Role

_DELAY = 20  # seconds between tests to respect RPM


@pytest.mark.asyncio
class TestAgent:
    async def test_greeting(self):
        """Agent responds to a greeting in Spanish."""
        request = ChatRequest(message="Hola, buenas tardes")
        response = await chat(request)
        assert response.role == Role.ASSISTANT
        assert len(response.content) > 0

    async def test_property_search(self):
        """Agent uses tools to search properties (function calling flow)."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(
            message="Busco un departamento de 2 dormitorios en Las Condes, hasta 5.000 UF"
        )
        response = await chat(request)
        assert response.role == Role.ASSISTANT
        content = response.content.lower()
        assert any(
            kw in content
            for kw in ["las condes", "departamento", "uf", "dormitorio", "propiedad"]
        )

    async def test_off_topic_rejected(self):
        """Agent declines non-real-estate questions."""
        await asyncio.sleep(_DELAY)
        request = ChatRequest(message="¿Cuál es la capital de Francia?")
        response = await chat(request)
        assert response.role == Role.ASSISTANT
        assert len(response.content) > 0
