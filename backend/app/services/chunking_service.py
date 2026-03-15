"""
Semantic chunking service.

Splits cleaned text into overlapping semantic chunks suitable for embedding
and quiz generation.
"""

from app.config import get_settings
from app.services.text_cleaning_service import TextCleaningService
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ChunkingService:
    """Breaks text into semantically meaningful chunks with configurable overlap."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.cleaner = TextCleaningService()

    def chunk_text(self, text: str, source_id: str) -> list[dict]:
        """
        Split text into semantic chunks.

        Strategy:
            1. Sentence-tokenize the full text.
            2. Greedily accumulate sentences until the word budget is reached.
            3. Slide the window back by `chunk_overlap` words for the next chunk.

        Args:
            text: Cleaned full document text.
            source_id: Identifier for the source document (used in chunk IDs).

        Returns:
            List of chunk dicts with keys: chunk_id, text, word_count.
        """
        sentences = self.cleaner.sentence_tokenize(text)
        if not sentences:
            return []

        chunks: list[dict] = []
        current_sentences: list[str] = []
        current_word_count = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())

            if current_word_count + sentence_words > self.chunk_size and current_sentences:
                # Emit current chunk
                chunk_text = " ".join(current_sentences)
                chunk_index += 1
                chunks.append(
                    {
                        "chunk_id": f"SRC_{source_id}_CH_{chunk_index:03d}",
                        "text": chunk_text,
                        "word_count": current_word_count,
                    }
                )

                # Overlap: keep some trailing sentences
                overlap_words = 0
                overlap_sentences: list[str] = []
                for s in reversed(current_sentences):
                    s_words = len(s.split())
                    if overlap_words + s_words > self.chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_words += s_words

                current_sentences = overlap_sentences
                current_word_count = overlap_words

            current_sentences.append(sentence)
            current_word_count += sentence_words

        # Final chunk
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunk_index += 1
            chunks.append(
                {
                    "chunk_id": f"SRC_{source_id}_CH_{chunk_index:03d}",
                    "text": chunk_text,
                    "word_count": current_word_count,
                }
            )

        logger.info(
            "Created %d chunks from text (chunk_size=%d, overlap=%d)",
            len(chunks),
            self.chunk_size,
            self.chunk_overlap,
        )
        return chunks
