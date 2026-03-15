"""
Answer API router.

Endpoints for submitting answers and viewing student progress.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.quiz_repository import QuizRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.answer_schema import (
    StudentProgressResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.adaptive_engine import AdaptiveEngine
from app.services.cache_service import progress_cache
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a student's answer, evaluate correctness, and update adaptive difficulty.

    Flow:
        1. Look up the question and its correct answer.
        2. Compare with the submitted answer.
        3. Record the StudentAnswer.
        4. Run the AdaptiveEngine to update StudentProgress.
    """
    quiz_repo = QuizRepository(db)
    student_repo = StudentRepository(db)
    engine = AdaptiveEngine()

    # ── 1. Fetch the question ────────────────────────────────────
    question = quiz_repo.get_question_by_id(request.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # ── 2. Evaluate answer ───────────────────────────────────────
    is_correct = request.selected_answer.strip().lower() == question.answer.strip().lower()

    # ── 3. Record the answer ─────────────────────────────────────
    student_repo.create_answer(
        student_id=request.student_id,
        question_id=request.question_id,
        selected_answer=request.selected_answer,
        is_correct=is_correct,
    )

    # ── 4. Update adaptive progress ──────────────────────────────
    progress = student_repo.get_or_create_progress(request.student_id)
    engine.update_progress(progress, is_correct)
    student_repo.update_progress(progress)
    # Invalidate cache so dashboard/analytics shows fresh data
    progress_cache.invalidate(f"progress:{request.student_id}")

    # ── 5. Build response ────────────────────────────────────────
    message = "Correct! Well done!" if is_correct else f"Incorrect. The correct answer is: {question.answer}"
    if is_correct and progress.correct_streak == 0:
        message += " Difficulty increased!"
    elif not is_correct and progress.wrong_streak == 0:
        message += " Difficulty decreased."

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.answer,
        current_difficulty=progress.current_difficulty,
        correct_streak=progress.correct_streak,
        wrong_streak=progress.wrong_streak,
        message=message,
    )


@router.get("/progress/{student_id}", response_model=StudentProgressResponse)
def get_progress(
    student_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the current progress for a student."""
    # Check cache first
    cache_key = f"progress:{student_id}"
    cached = progress_cache.get(cache_key)
    if cached:
        return cached

    student_repo = StudentRepository(db)
    progress = student_repo.get_or_create_progress(student_id)
    engine = AdaptiveEngine()

    response = StudentProgressResponse.model_validate(progress)
    response.accuracy = engine.get_accuracy(progress)

    # Cache for 30 seconds
    progress_cache.set(cache_key, response, ttl=30)
    return response
