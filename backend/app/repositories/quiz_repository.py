"""
Quiz repository — data access for quiz questions.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.quiz_question import QuizQuestion
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QuizRepository:
    """CRUD operations for QuizQuestion."""

    def __init__(self, db: Session):
        self.db = db

    def create_questions(self, questions: list[QuizQuestion]) -> list[QuizQuestion]:
        """Bulk-insert quiz questions."""
        self.db.add_all(questions)
        self.db.commit()
        for q in questions:
            self.db.refresh(q)
        logger.info("Inserted %d quiz questions", len(questions))
        return questions

    def get_question_by_id(self, question_id: int) -> Optional[QuizQuestion]:
        return self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()

    def get_questions_by_chunk(self, chunk_id: int) -> list[QuizQuestion]:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.source_chunk_id == chunk_id)
            .all()
        )

    def get_questions(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        source_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[QuizQuestion], int]:
        """
        Retrieve quiz questions with optional topic/difficulty/source filters.

        Returns (questions, total_count).
        """
        query = self.db.query(QuizQuestion)

        if source_id:
            from app.models.content_chunk import ContentChunk
            query = query.join(ContentChunk).filter(ContentChunk.source_id == source_id)

        if topic:
            # Join through chunk to filter by topic
            from app.models.content_chunk import ContentChunk
            from sqlalchemy import func

            query = query.join(ContentChunk).filter(
                func.lower(ContentChunk.topic).contains(topic.lower())
            )

        if difficulty:
            query = query.filter(QuizQuestion.difficulty == difficulty.lower())

        total = query.count()
        questions = query.offset(offset).limit(limit).all()
        return questions, total

    def get_all_question_embeddings(self) -> list[dict]:
        """Return question text + id for duplicate detection."""
        results = self.db.query(QuizQuestion.id, QuizQuestion.question).all()
        return [{"id": r.id, "question": r.question} for r in results]
