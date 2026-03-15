"""
Quiz API router.

Endpoints for generating and retrieving quiz questions.
"""

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.quiz_question import QuizQuestion
from app.repositories.content_repository import ContentRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz_schema import (
    DifficultyLevel,
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizListResponse,
    QuizQuestionResponse,
)
from app.services.embedding_service import EmbeddingService
from app.services.quiz_generation_service import QuizGenerationService
from app.utils.duplicate_detection import is_duplicate
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post("/generate-quiz", response_model=GenerateQuizResponse, status_code=201)
def generate_quiz(
    request: GenerateQuizRequest,
    db: Session = Depends(get_db),
):
    """
    Generate quiz questions from stored content chunks using the LLM.

    Selects chunks based on optional topic/source filters, sends them
    to the LLM, validates responses, checks for duplicates, and stores results.
    """
    content_repo = ContentRepository(db)
    quiz_repo = QuizRepository(db)

    # ── Select chunks ────────────────────────────────────────────
    if request.topic:
        chunks = content_repo.get_chunks_by_topic(request.topic, limit=request.num_chunks)
    elif request.source_id:
        chunks = content_repo.get_chunks_by_source(request.source_id)[:request.num_chunks]
    else:
        chunks = content_repo.get_random_chunks(limit=request.num_chunks)

    if not chunks:
        raise HTTPException(status_code=404, detail="No content chunks found matching the criteria.")

    # ── Get existing question embeddings for duplicate detection ─
    embedding_service = EmbeddingService()
    existing_q = quiz_repo.get_all_question_embeddings()
    existing_embeddings: list[list[float]] = []
    try:
        if existing_q:
            existing_embeddings = embedding_service.generate_embeddings_batch(
                [q["question"] for q in existing_q]
            )
    except RuntimeError:
        logger.warning("Could not generate embeddings for duplicate detection")

    # ── Generate questions chunk-by-chunk ─────────────────────────
    # ── Initialize LLM service ────────────────────────────────────
    try:
        quiz_service = QuizGenerationService()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    all_questions: list[QuizQuestion] = []

    for idx, chunk in enumerate(chunks):
        # Rate-limit delay between chunks (skip for the first chunk)
        if idx > 0:
            time.sleep(5)

        # Determine subject/grade from source document
        source = chunk.source
        subject = source.subject if source else "General"
        grade = source.grade if source and source.grade else 5
        difficulty = request.difficulty.value if request.difficulty else "medium"

        try:
            raw_questions = quiz_service.generate_questions(
                text_chunk=chunk.text,
                subject=subject,
                grade=grade,
                difficulty=difficulty,
            )
        except RuntimeError as exc:
            error_msg = str(exc)
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="LLM rate limit exceeded. Please wait a minute and try again.",
                )
            logger.error("LLM generation failed for chunk %s: %s", chunk.chunk_id, exc)
            continue
        except Exception as exc:
            logger.error("LLM generation failed for chunk %s: %s", chunk.chunk_id, exc)
            continue

        for q in raw_questions:
            # ── Duplicate detection ──────────────────────────────
            try:
                q_embedding = embedding_service.generate_embedding(q["question"])
                if existing_embeddings and is_duplicate(q_embedding, existing_embeddings):
                    logger.info("Skipping duplicate question: %s", q["question"][:60])
                    continue
                existing_embeddings.append(q_embedding)
            except RuntimeError:
                pass  # If embedding fails, skip dedup check

            # ── Quality scoring (optional, skip by default) ───────
            quality_score = None
            if not settings.SKIP_QUALITY_SCORING:
                time.sleep(2)  # Delay to avoid rate limiting
                quality = quiz_service.score_question_quality(
                    question=q["question"],
                    question_type=q["type"],
                    options=q.get("options"),
                    answer=q["answer"],
                    source_text=chunk.text,
                )
                quality_score = quality.get("score")

            question_model = QuizQuestion(
                question=q["question"],
                type=q["type"],
                options=q.get("options"),
                answer=q["answer"],
                difficulty=q.get("difficulty", difficulty),
                source_chunk_id=chunk.id,
                quality_score=quality_score,
            )
            all_questions.append(question_model)

    if not all_questions:
        raise HTTPException(status_code=500, detail="Failed to generate any quiz questions.")

    stored = quiz_repo.create_questions(all_questions)
    logger.info("Stored %d quiz questions", len(stored))

    return GenerateQuizResponse(
        questions_generated=len(stored),
        questions=[QuizQuestionResponse.model_validate(q) for q in stored],
    )


@router.get("/quiz", response_model=QuizListResponse)
def get_quiz(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (easy/medium/hard)"),
    source_id: Optional[int] = Query(None, description="Filter by source document ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieve quiz questions with optional topic, difficulty, and source filters.
    """
    quiz_repo = QuizRepository(db)
    questions, total = quiz_repo.get_questions(
        topic=topic, difficulty=difficulty, source_id=source_id, limit=limit, offset=offset
    )
    return QuizListResponse(
        total=total,
        questions=[QuizQuestionResponse.model_validate(q) for q in questions],
    )
