import logging

from fastapi import APIRouter, HTTPException

from app.core.agent import chat
from app.schemas.conversation import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Process a user message and return an AI-generated response."""
    try:
        return await chat(request)
    except Exception as e:
        error_str = str(e)
        logger.exception("Chat endpoint error")

        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            # Distinguish daily quota vs per-minute rate limit
            if "PerDay" in error_str:
                raise HTTPException(
                    status_code=429,
                    detail="Se alcanzó el límite diario de consultas de la IA. La cuota se reinicia mañana. Puedes generar una nueva API key en ai.google.dev para continuar.",
                ) from e
            raise HTTPException(
                status_code=429,
                detail="Demasiadas consultas por minuto. Espera unos segundos e intenta de nuevo.",
            ) from e

        if "503" in error_str or "UNAVAILABLE" in error_str:
            raise HTTPException(
                status_code=503,
                detail="El servicio de IA está temporalmente saturado. Intenta de nuevo en unos segundos.",
            ) from e

        raise HTTPException(
            status_code=500,
            detail="Error procesando tu mensaje. Por favor intenta de nuevo.",
        ) from e
