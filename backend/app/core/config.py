# config.py
# Purpose: Central configuration management using Pydantic Settings.
# Responsibilities:
#   - Load all environment variables from .env
#   - Validate types at startup and export a singleton settings instance
# DO NOT: Hardcode any config values directly in code.
# DO NOT: Import this from models or DB files to prevent circular imports.

from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "CoFoundr"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ─── Vector DB ────────────────────────────────────────────────────────────
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # ─── AI Providers ─────────────────────────────────────────────────────────
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    TAVILY_API_KEY: str

    # ─── Auth ─────────────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # ─── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: Any = ["http://localhost:3000"]

    # ─── File Upload ──────────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 10
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: str | List[str]) -> List[str]:
        """Parse comma-separated origins string into list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# ─── Singleton instance ───────────────────────────────────────────────────────
settings = Settings()
