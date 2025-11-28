"""
AI Provider Abstraction Layer
Supports: Ollama (local/free), OpenAI, Google Gemini

Configuration via environment variables:
- AI_PROVIDER: "ollama" | "openai" | "gemini" (default: "ollama")
- AI_MODEL: Model name (default depends on provider)
- OLLAMA_BASE_URL: Ollama server URL (default: "http://ollama:11434")
- OPENAI_API_KEY: OpenAI API key (required for openai provider)
- GEMINI_API_KEY: Google Gemini API key (required for gemini provider)
"""

import os
import httpx
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AIClassificationResult(BaseModel):
    """Standard result format for instrument classification"""
    system: str = "Manual"
    io_type: str = "AI"
    suggested_area: str | None = None
    confidence: float = 0.0
    provider: str = "none"
    error: str | None = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    async def classify_instrument(
        self, tag: str, description: str
    ) -> AIClassificationResult:
        """Classify an instrument based on tag and description"""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check if the provider is available"""
        pass


class OllamaProvider(AIProvider):
    """
    Ollama - Free, local AI inference
    Recommended models: llama3.2, mistral, codellama
    """

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = os.getenv("AI_MODEL", "llama3.2")

    async def classify_instrument(
        self, tag: str, description: str
    ) -> AIClassificationResult:
        prompt = f"""Analyze this industrial instrument and return JSON only.
Tag: "{tag}"
Description: "{description}"

Return exactly this JSON format:
{{"system": "string (e.g., Grinding, Crushing, Flotation, Utilities)", "io_type": "string (AI, AO, DI, DO, PROFIBUS, ETHERNET)", "suggested_area": "string or null", "confidence": number 0-1}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                result = eval(data.get("response", "{}"))  # Ollama returns string

                return AIClassificationResult(
                    system=result.get("system", "Manual"),
                    io_type=result.get("io_type", "AI"),
                    suggested_area=result.get("suggested_area"),
                    confidence=result.get("confidence", 0.8),
                    provider="ollama"
                )
        except Exception as e:
            logger.error(f"Ollama classification failed: {e}")
            return AIClassificationResult(
                provider="ollama",
                error=str(e)
            )

    async def health_check(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                return {
                    "status": "healthy",
                    "provider": "ollama",
                    "base_url": self.base_url,
                    "model": self.model,
                    "available_models": [m["name"] for m in models]
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "ollama",
                "error": str(e)
            }


class OpenAIProvider(AIProvider):
    """
    OpenAI - Paid API
    Models: gpt-4o-mini (cheap), gpt-4o (better)
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.base_url = "https://api.openai.com/v1"

    async def classify_instrument(
        self, tag: str, description: str
    ) -> AIClassificationResult:
        if not self.api_key:
            return AIClassificationResult(
                provider="openai",
                error="OPENAI_API_KEY not configured"
            )

        prompt = f"""Analyze this industrial instrument. Return JSON only.
Tag: "{tag}"
Description: "{description}"

JSON format: {{"system": "string", "io_type": "AI|AO|DI|DO|PROFIBUS|ETHERNET", "suggested_area": "string|null", "confidence": 0-1}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are an industrial automation expert. Return only valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                result = eval(content)

                return AIClassificationResult(
                    system=result.get("system", "Manual"),
                    io_type=result.get("io_type", "AI"),
                    suggested_area=result.get("suggested_area"),
                    confidence=result.get("confidence", 0.9),
                    provider="openai"
                )
        except Exception as e:
            logger.error(f"OpenAI classification failed: {e}")
            return AIClassificationResult(
                provider="openai",
                error=str(e)
            )

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "provider": "openai",
                "error": "OPENAI_API_KEY not set"
            }
        return {
            "status": "configured",
            "provider": "openai",
            "model": self.model
        }


class GeminiProvider(AIProvider):
    """
    Google Gemini - Paid API (free tier available)
    Models: gemini-1.5-flash (cheap), gemini-1.5-pro (better)
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "gemini-1.5-flash")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def classify_instrument(
        self, tag: str, description: str
    ) -> AIClassificationResult:
        if not self.api_key:
            return AIClassificationResult(
                provider="gemini",
                error="GEMINI_API_KEY not configured"
            )

        prompt = f"""Analyze this industrial instrument and return JSON only.
Tag: "{tag}"
Description: "{description}"

Return exactly: {{"system": "string", "io_type": "AI|AO|DI|DO|PROFIBUS|ETHERNET", "suggested_area": "string|null", "confidence": 0-1}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    params={"key": self.api_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.3
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                result = eval(content)

                return AIClassificationResult(
                    system=result.get("system", "Manual"),
                    io_type=result.get("io_type", "AI"),
                    suggested_area=result.get("suggested_area"),
                    confidence=result.get("confidence", 0.85),
                    provider="gemini"
                )
        except Exception as e:
            logger.error(f"Gemini classification failed: {e}")
            return AIClassificationResult(
                provider="gemini",
                error=str(e)
            )

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "provider": "gemini",
                "error": "GEMINI_API_KEY not set"
            }
        return {
            "status": "configured",
            "provider": "gemini",
            "model": self.model
        }


class NoOpProvider(AIProvider):
    """Fallback when AI is disabled"""

    async def classify_instrument(
        self, tag: str, description: str
    ) -> AIClassificationResult:
        return AIClassificationResult(
            system="Manual",
            io_type="AI",
            confidence=0.0,
            provider="none",
            error="AI classification disabled"
        )

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "disabled",
            "provider": "none"
        }


# Provider factory
_providers: dict[str, type[AIProvider]] = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "none": NoOpProvider
}

_current_provider: AIProvider | None = None


def get_ai_provider() -> AIProvider:
    """Get the configured AI provider (singleton)"""
    global _current_provider

    if _current_provider is None:
        provider_name = os.getenv("AI_PROVIDER", "ollama").lower()
        provider_class = _providers.get(provider_name, NoOpProvider)
        _current_provider = provider_class()
        logger.info(f"AI Provider initialized: {provider_name}")

    return _current_provider


def reset_provider():
    """Reset provider (useful for testing or runtime config change)"""
    global _current_provider
    _current_provider = None


def get_available_providers() -> list[str]:
    """List available AI providers"""
    return list(_providers.keys())
