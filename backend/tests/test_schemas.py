"""Tests for Pydantic schemas — validates contracts are correct."""
import pytest
from pydantic import ValidationError

from app.schemas.conversation import ChatRequest, ChatResponse, Message, Role


class TestRole:
    def test_valid_roles(self):
        assert Role.USER == "user"
        assert Role.ASSISTANT == "assistant"


class TestMessage:
    def test_valid_message(self):
        msg = Message(role=Role.USER, content="Hola")
        assert msg.role == Role.USER
        assert msg.content == "Hola"

    def test_assistant_message(self):
        msg = Message(role=Role.ASSISTANT, content="¡Hola! ¿En qué puedo ayudarte?")
        assert msg.role == Role.ASSISTANT


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(message="Busco un depto en Las Condes")
        assert req.message == "Busco un depto en Las Condes"
        assert req.history == []

    def test_request_with_history(self):
        history = [
            Message(role=Role.USER, content="Hola"),
            Message(role=Role.ASSISTANT, content="¡Hola!"),
        ]
        req = ChatRequest(message="Busco casa", history=history)
        assert len(req.history) == 2

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_long_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 2001)

    def test_serialization_roundtrip(self):
        req = ChatRequest(
            message="test",
            history=[Message(role=Role.USER, content="prev")],
        )
        data = req.model_dump()
        restored = ChatRequest(**data)
        assert restored.message == req.message
        assert len(restored.history) == 1


class TestChatResponse:
    def test_valid_response(self):
        res = ChatResponse(content="Encontré 3 propiedades")
        assert res.role == Role.ASSISTANT
        assert res.content == "Encontré 3 propiedades"

    def test_json_output(self):
        res = ChatResponse(content="test")
        data = res.model_dump()
        assert data["role"] == "assistant"
        assert data["content"] == "test"
