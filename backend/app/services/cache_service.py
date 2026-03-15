"""
In-memory caching service for quiz questions and student progress.

Provides a simple TTL-based cache to reduce database and API calls.
"""

import time
from typing import Any, Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Simple in-memory TTL cache."""

    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes).
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if it exists and hasn't expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires"]:
            del self._cache[key]
            return None
        logger.debug("Cache hit: %s", key)
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cached value with TTL."""
        self._cache[key] = {
            "value": value,
            "expires": time.time() + (ttl or self._default_ttl),
        }
        logger.debug("Cache set: %s (ttl=%d)", key, ttl or self._default_ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific cache entry."""
        self._cache.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        """Remove all cache entries matching a prefix."""
        keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._cache[k]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache singleton
quiz_cache = CacheService(default_ttl=300)     # 5 min for quiz data
progress_cache = CacheService(default_ttl=30)  # 30 sec for progress (near real-time)
