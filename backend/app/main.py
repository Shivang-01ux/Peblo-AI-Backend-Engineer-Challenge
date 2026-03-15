"""
FastAPI application entrypoint.

Configures CORS, includes API routers, and creates DB tables on startup.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api.ingest_api import router as ingest_router
from app.api.quiz_api import router as quiz_router
from app.api.answer_api import router as answer_router
from app.utils.logger import get_logger

# Ensure all models are imported so Base.metadata knows about them
import app.models  # noqa: F401

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables and upload directory on startup."""
    logger.info("Starting Peblo AI Mini v%s", settings.APP_VERSION)
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Database tables created and upload directory ready.")
    yield
    logger.info("Shutting down Peblo AI Mini.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered educational platform backend — "
        "Content Ingestion + Adaptive Quiz Engine"
    ),
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(quiz_router, tags=["Quiz"])
app.include_router(answer_router, tags=["Answers"])


@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/features", tags=["Health"])
def feature_status():
    """Shows which optional features are currently active."""
    return {
        "duplicate_question_detection": {
            "enabled": True,
            "method": "Cosine similarity on SentenceTransformer embeddings",
            "threshold": 0.90,
            "file": "app/utils/duplicate_detection.py",
        },
        "question_validation": {
            "enabled": True,
            "method": "JSON schema validation of LLM output (type, options, answer checks)",
            "file": "app/services/quiz_generation_service.py → _validate_question()",
        },
        "embeddings_for_similarity": {
            "enabled": True,
            "model": settings.EMBEDDING_MODEL,
            "method": "SentenceTransformer local model for text chunk and question embeddings",
            "file": "app/services/embedding_service.py",
        },
        "caching": {
            "enabled": True,
            "method": "In-memory TTL cache (progress: 30s, quiz: 5min)",
            "file": "app/services/cache_service.py",
        },
        "quality_scoring": {
            "enabled": not settings.SKIP_QUALITY_SCORING,
            "method": "LLM rates each question 1-10 with retry logic",
            "note": "Currently skipped for speed — set SKIP_QUALITY_SCORING=false to enable",
            "file": "app/services/quiz_generation_service.py → score_question_quality()",
        },
        "adaptive_difficulty": {
            "enabled": True,
            "method": "2 correct → level up, 2 wrong → level down",
            "levels": ["easy", "medium", "hard"],
            "file": "app/services/adaptive_engine.py",
        },
    }
