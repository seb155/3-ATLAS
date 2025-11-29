"""
AI Classification Router
Provides endpoints for AI-powered instrument classification

Endpoints:
- POST /api/v1/ai/classify - Classify an instrument
- GET /api/v1/ai/health - Check AI provider health
- GET /api/v1/ai/providers - List available providers
- POST /api/v1/ai/switch - Switch AI provider (admin only)
"""

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_provider import (
    get_ai_provider,
    get_available_providers,
    reset_provider,
)

router = APIRouter()


class ClassifyRequest(BaseModel):
    """Request body for instrument classification"""
    tag: str = Field(..., min_length=1, max_length=100, description="Instrument tag")
    description: str = Field(..., min_length=1, max_length=500, description="Instrument description")


class ClassifyResponse(BaseModel):
    """Response for instrument classification"""
    system: str
    io_type: str
    suggested_area: str | None
    confidence: float
    provider: str
    error: str | None = None


class SwitchProviderRequest(BaseModel):
    """Request to switch AI provider"""
    provider: str = Field(..., description="Provider name: ollama, openai, gemini, none")
    model: str | None = Field(None, description="Optional model override")
    api_key: str | None = Field(None, description="Optional API key (for openai/gemini)")


class ProviderInfo(BaseModel):
    """Information about an AI provider"""
    name: str
    status: str
    model: str | None = None
    requires_api_key: bool = False
    description: str


@router.post("/classify", response_model=ClassifyResponse)
async def classify_instrument(request: ClassifyRequest):
    """
    Classify an instrument using the configured AI provider.

    Returns system, IO type, and suggested area based on tag and description.
    """
    provider = get_ai_provider()
    result = await provider.classify_instrument(request.tag, request.description)

    return ClassifyResponse(
        system=result.system,
        io_type=result.io_type,
        suggested_area=result.suggested_area,
        confidence=result.confidence,
        provider=result.provider,
        error=result.error
    )


@router.get("/health")
async def ai_health():
    """
    Check the health of the current AI provider.

    Returns provider status, model info, and any errors.
    """
    provider = get_ai_provider()
    return await provider.health_check()


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers():
    """
    List all available AI providers with their status.
    """
    current_provider = os.getenv("AI_PROVIDER", "ollama").lower()

    providers_info = [
        ProviderInfo(
            name="ollama",
            status="active" if current_provider == "ollama" else "available",
            model=os.getenv("AI_MODEL", "llama3.2") if current_provider == "ollama" else "llama3.2",
            requires_api_key=False,
            description="Local AI inference - FREE, requires Ollama server"
        ),
        ProviderInfo(
            name="openai",
            status="active" if current_provider == "openai" else ("configured" if os.getenv("OPENAI_API_KEY") else "available"),
            model=os.getenv("AI_MODEL", "gpt-4o-mini") if current_provider == "openai" else "gpt-4o-mini",
            requires_api_key=True,
            description="OpenAI GPT models - PAID, cloud-based"
        ),
        ProviderInfo(
            name="gemini",
            status="active" if current_provider == "gemini" else ("configured" if os.getenv("GEMINI_API_KEY") else "available"),
            model=os.getenv("AI_MODEL", "gemini-1.5-flash") if current_provider == "gemini" else "gemini-1.5-flash",
            requires_api_key=True,
            description="Google Gemini - PAID (free tier available), cloud-based"
        ),
        ProviderInfo(
            name="none",
            status="active" if current_provider == "none" else "available",
            model=None,
            requires_api_key=False,
            description="Disabled - No AI classification, manual mode only"
        ),
    ]

    return providers_info


@router.post("/switch")
async def switch_provider(request: SwitchProviderRequest):
    """
    Switch the AI provider at runtime.

    Note: This changes environment variables and resets the provider singleton.
    Changes persist only for the current process lifetime.
    For permanent changes, update the environment configuration.
    """
    available = get_available_providers()
    if request.provider not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Available: {available}"
        )

    # Update environment variables
    os.environ["AI_PROVIDER"] = request.provider

    if request.model:
        os.environ["AI_MODEL"] = request.model

    if request.api_key:
        if request.provider == "openai":
            os.environ["OPENAI_API_KEY"] = request.api_key
        elif request.provider == "gemini":
            os.environ["GEMINI_API_KEY"] = request.api_key

    # Reset the singleton to pick up new config
    reset_provider()

    # Verify the new provider
    provider = get_ai_provider()
    health = await provider.health_check()

    return {
        "message": f"Switched to {request.provider}",
        "health": health
    }


@router.get("/config")
async def get_config():
    """
    Get current AI configuration (without sensitive data).
    """
    return {
        "provider": os.getenv("AI_PROVIDER", "ollama"),
        "model": os.getenv("AI_MODEL", "auto"),
        "ollama_url": os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
    }
