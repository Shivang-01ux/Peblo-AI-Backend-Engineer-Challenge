"""
Rule-based difficulty classifier for content and questions.
"""

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Difficulty constants ─────────────────────────────────────────
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
DIFFICULTY_ORDER = {level: idx for idx, level in enumerate(DIFFICULTY_LEVELS)}


def classify_text_difficulty(text: str, grade: int | None = None) -> str:
    """
    Heuristic difficulty classification based on text complexity.

    Uses average word length, sentence count, and grade level as signals.
    """
    words = text.split()
    word_count = len(words)

    if word_count == 0:
        return "easy"

    avg_word_length = sum(len(w) for w in words) / word_count
    sentence_count = text.count(".") + text.count("!") + text.count("?")
    words_per_sentence = word_count / max(sentence_count, 1)

    score = 0

    # Word length complexity
    if avg_word_length > 7:
        score += 2
    elif avg_word_length > 5:
        score += 1

    # Sentence complexity
    if words_per_sentence > 20:
        score += 2
    elif words_per_sentence > 12:
        score += 1

    # Grade adjustment
    if grade:
        if grade >= 9:
            score += 2
        elif grade >= 5:
            score += 1

    if score >= 4:
        return "hard"
    elif score >= 2:
        return "medium"
    return "easy"


def next_difficulty(current: str) -> str:
    """Return one level harder, capped at 'hard'."""
    idx = DIFFICULTY_ORDER.get(current, 0)
    new_idx = min(idx + 1, len(DIFFICULTY_LEVELS) - 1)
    return DIFFICULTY_LEVELS[new_idx]


def previous_difficulty(current: str) -> str:
    """Return one level easier, capped at 'easy'."""
    idx = DIFFICULTY_ORDER.get(current, 0)
    new_idx = max(idx - 1, 0)
    return DIFFICULTY_LEVELS[new_idx]
