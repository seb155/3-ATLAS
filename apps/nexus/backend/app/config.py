from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application configuration settings.
    Loads from environment variables or .env file.

    Workspace Integration:
    - database_url: Main Nexus database (nexus)
    - auth_database_url: Shared workspace_auth schema (for SSO)
    - redis_url: Shared Redis with key prefixing
    - secret_key: Shared across workspace apps for JWT validation
    """

    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================

    # Main application database (nexus)
    database_url: str

    # Shared authentication database (workspace_auth schema)
    # If not set, falls back to database_url
    auth_database_url: Optional[str] = None

    # Legacy database settings (for compatibility)
    postgres_server: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None

    # ========================================================================
    # REDIS CONFIGURATION
    # ========================================================================

    redis_url: str
    redis_key_prefix: str = "nexus:"  # Namespace for shared Redis

    # ========================================================================
    # JWT AUTHENTICATION (Shared across workspace apps)
    # ========================================================================

    secret_key: str  # MUST match across workspace apps for SSO
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # ========================================================================
    # CORS CONFIGURATION
    # ========================================================================

    cors_origins: str = "http://localhost:5173,https://nexus.localhost"

    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================

    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    app_name: str = "Nexus"
    app_version: str = "0.2.0"

    # ========================================================================
    # LOGGING (Loki integration)
    # ========================================================================

    loki_url: Optional[str] = None

    # ========================================================================
    # TRILIUM INTEGRATION
    # ========================================================================

    trilium_etapi_url: Optional[str] = None  # e.g., https://notes.s-gagnon.com
    trilium_etapi_token: Optional[str] = None
    trilium_sync_interval: int = 60  # seconds between sync checks

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def effective_auth_database_url(self) -> str:
        """
        Returns auth_database_url if set, otherwise database_url.
        This allows using the same database for auth in standalone mode.
        """
        return self.auth_database_url or self.database_url

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for extensibility


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use this dependency in FastAPI routes.

    Example:
        from fastapi import Depends

        @app.get("/info")
        def get_info(settings: Settings = Depends(get_settings)):
            return {"environment": settings.environment}
    """
    return Settings()
