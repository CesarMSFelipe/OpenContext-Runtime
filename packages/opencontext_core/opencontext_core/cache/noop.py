"""No-op cache implementations."""

from __future__ import annotations

from opencontext_core.cache.base import CacheKey, ResponseCache


class NoOpCache(ResponseCache):
    """Cache implementation that never stores values."""

    def get(self, key: CacheKey) -> str | None:
        """Always return a cache miss."""

        del key
        return None

    def set(self, key: CacheKey, value: str) -> None:
        """Ignore stored values."""

        del key, value
