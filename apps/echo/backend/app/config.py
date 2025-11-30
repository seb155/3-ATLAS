"""
ECHO Configuration Settings.

Environment variables with defaults for development.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "ECHO"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    # Database (FORGE PostgreSQL)
    database_url: str = "postgresql://postgres:postgres@forge-postgres:5432/echo"
    postgres_server: str = "forge-postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "echo"

    # Redis (FORGE Redis)
    redis_url: str = "redis://forge-redis:6379"
    redis_key_prefix: str = "echo:"

    # JWT Authentication (shared with AXIOM workspace)
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS
    cors_origins: str = "http://localhost:7200,http://localhost:5173"

    # Whisper Configuration
    whisper_device: str = "auto"  # auto, npu, gpu, cpu
    whisper_model: str = "base"  # CPU fallback model
    whisper_model_npu: str = "medium"  # NPU model (faster with BFP16)
    whisper_compute_type: str = "int8"  # float16 for GPU, int8 for CPU, bfp16 for NPU
    whisper_precision: str = "bfp16"  # NPU native precision

    # Audio Configuration
    audio_storage_path: str = "/app/data"
    default_sample_rate: int = 44100
    default_language: str = "auto"  # auto, fr, en

    # Logging
    loki_url: Optional[str] = "http://loki:3100"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
