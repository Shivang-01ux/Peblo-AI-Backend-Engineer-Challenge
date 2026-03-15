"""
Embedding service.

Generates dense vector embeddings using Sentence Transformers (local)
or OpenAI Embeddings API.
"""

from typing import Optional

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Lazy-loaded model singleton
_model = None


def _get_local_model():
    """Lazy-load the SentenceTransformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


class EmbeddingService:
    """Generate embeddings for text chunks and questions."""

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text string.

        Uses the local Sentence Transformers model by default.
        """
        if not text.strip():
            return []

        try:
            model = _get_local_model()
            embedding = model.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as exc:
            logger.exception("Embedding generation failed for text snippet")
            raise RuntimeError(f"Embedding generation failed: {exc}") from exc

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.

        More efficient than calling generate_embedding in a loop.
        """
        if not texts:
            return []

        try:
            model = _get_local_model()
            embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
            return [e.tolist() for e in embeddings]
        except Exception as exc:
            logger.exception("Batch embedding generation failed")
            raise RuntimeError(f"Batch embedding failed: {exc}") from exc
