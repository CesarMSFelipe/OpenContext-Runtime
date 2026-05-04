"""Exact in-memory prompt/response cache."""

from __future__ import annotations

from opencontext_core.cache.base import CacheKey, ResponseCache, cache_allowed_for_classifications
from opencontext_core.safety.redaction import SinkGuard


class ExactPromptCache(ResponseCache):
    """Simple exact cache keyed by deterministic cache fields."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}

    def get(self, key: CacheKey) -> str | None:
        """Return a cached value if present."""

        return self._values.get(key.value)

    def set(self, key: CacheKey, value: str) -> None:
        """Store a cached value."""

        if not cache_allowed_for_classifications(key.classifications):
            return
        safe_value, _ = SinkGuard().redact(value)
        self._values[key.value] = safe_value
