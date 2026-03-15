"""
Duplicate question detection using cosine similarity on embeddings.
"""

import numpy as np
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def is_duplicate(
    new_embedding: list[float],
    existing_embeddings: list[list[float]],
    threshold: float = 0.90,
) -> bool:
    """
    Check if a question embedding is too similar to any existing embedding.

    Args:
        new_embedding: Embedding vector of the new question.
        existing_embeddings: List of embedding vectors for existing questions.
        threshold: Similarity threshold above which a question is duplicate.

    Returns:
        True if a duplicate is detected.
    """
    for existing in existing_embeddings:
        sim = cosine_similarity(new_embedding, existing)
        if sim >= threshold:
            logger.debug("Duplicate detected with similarity %.4f", sim)
            return True
    return False


def find_most_similar(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Find the top-k most similar items by cosine similarity.

    Args:
        query_embedding: The query vector.
        candidates: List of dicts with 'embedding' key.
        top_k: Number of results to return.

    Returns:
        Sorted list of candidates with added 'similarity' key.
    """
    scored = []
    for item in candidates:
        if item.get("embedding"):
            sim = cosine_similarity(query_embedding, item["embedding"])
            scored.append({**item, "similarity": sim})

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]
