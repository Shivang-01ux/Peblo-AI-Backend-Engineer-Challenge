"""
Application configuration module.

Loads settings from environment variables / .env file using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Peblo AI Mini"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://peblo:peblo@localhost:5432/peblo_db"

    # ── Redis (optional) ────────────────────────────────────────
    REDIS_URL: str = ""
    CACHE_TTL: int = 300  # seconds

    # ── LLM ──────────────────────────────────────────────────────
    LLM_PROVIDER: str = "openai"  # openai | anthropic | gemini
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    SKIP_QUALITY_SCORING: bool = True  # Skip per-question LLM quality scoring

    # ── Embedding ────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Chunking ─────────────────────────────────────────────────
    CHUNK_SIZE: int = 500  # tokens
    CHUNK_OVERLAP: int = 50

    # ── Upload ───────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    # ── Duplicate Detection ──────────────────────────────────────
    SIMILARITY_THRESHOLD: float = 0.90

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()
