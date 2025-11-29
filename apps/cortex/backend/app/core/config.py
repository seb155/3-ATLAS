"""
CORTEX Configuration

Environment-based settings using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cortex"

    # Cache
    REDIS_URL: str = "redis://localhost:6379/2"

    # AI Providers
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # External Services (ai-sandbox)
    LITELLM_URL: str = "http://litellm:4000"
    OLLAMA_URL: str = "http://ollama:11434"
    CHROMADB_URL: str = "http://chromadb:8000"
    LANGFUSE_URL: str = "http://langfuse-server:3000"

    # Context Settings
    MAX_CONTEXT_TOKENS: int = 100000
    HOT_CACHE_SIZE: int = 50000
    WARM_CACHE_SIZE: int = 100000

    # Model defaults
    DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:4000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
