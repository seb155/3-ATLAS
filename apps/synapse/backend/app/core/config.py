import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AXOIQ SYNAPSE"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "synapse"
    POSTGRES_PORT: str = "5432"

    # Analytics / Owner database (read-only usage)
    ANALYTICS_POSTGRES_SERVER: str = "db"
    ANALYTICS_POSTGRES_USER: str = "postgres"
    ANALYTICS_POSTGRES_PASSWORD: str = "postgres"
    ANALYTICS_POSTGRES_DB: str = "synapse_analytics"
    ANALYTICS_POSTGRES_PORT: str = "5432"

    # Auth - SECURITY: No default for SECRET_KEY in production
    # Generate with: openssl rand -hex 32
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS - Comma-separated list of allowed origins for production
    ALLOWED_ORIGINS: str = ""

    DATABASE_URL: str | None = None
    ANALYTICS_DATABASE_URL: str | None = None

    # AI Provider Configuration
    # Options: "ollama" (free/local), "openai", "gemini", "none"
    AI_PROVIDER: str = "ollama"
    AI_MODEL: str | None = None  # Auto-select based on provider
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def ANALYTICS_SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.ANALYTICS_DATABASE_URL:
            return self.ANALYTICS_DATABASE_URL
        return (
            f"postgresql://{self.ANALYTICS_POSTGRES_USER}:{self.ANALYTICS_POSTGRES_PASSWORD}"
            f"@{self.ANALYTICS_POSTGRES_SERVER}:{self.ANALYTICS_POSTGRES_PORT}/{self.ANALYTICS_POSTGRES_DB}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
