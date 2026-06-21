"""CCR Cache — Reversible Compression Cache.

Caches original content before compression, keyed by SHA256 hash.
The LLM can retrieve originals on demand via a tool call, enabling
lossy compression without information loss.

The cache is local (SQLite or in-memory), has a TTL, and is capped
at a maximum number of entries. This is a write-through cache:
content is stored before compression, and the hash is embedded in
the compressed output as a retrieval token.
"""

from __future__ import annotations

import hashlib
import sqlite3
import threading
from collections import OrderedDict
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class CCREntry:
    """A single entry in the CCR cache."""

    content_hash: str  # SHA256 of original content
    content_type: str  # "json", "code", "prose", etc.
    original: str  # The original (uncompressed) content
    compressed: str  # The compressed version sent to the LLM
    stored_at: str  # ISO timestamp
    expires_at: str  # ISO timestamp (stored_at + TTL)
    access_count: int = 0


@dataclass
class CCRStats:
    """Statistics for the CCR cache."""

    entries: int
    max_entries: int
    ttl_seconds: int
    hits: int
    misses: int
    evictions: int


class CCRCacheBackend:
    """Abstract CCR storage backend."""

    def get(self, content_hash: str) -> CCREntry | None:
        raise NotImplementedError

    def put(self, entry: CCREntry) -> None:
        raise NotImplementedError

    def remove(self, content_hash: str) -> None:
        raise NotImplementedError

    def stats(self) -> CCRStats:
        raise NotImplementedError

    def evict_expired(self) -> int:
        raise NotImplementedError


class MemoryCCRBackend(CCRCacheBackend):
    """In-memory CCR backend (fastest, no persistence)."""

    def __init__(self, max_entries: int = 500, ttl_seconds: int = 300) -> None:
        self._max = max_entries
        self._ttl = ttl_seconds
        self._entries: OrderedDict[str, CCREntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = threading.RLock()

    def get(self, content_hash: str) -> CCREntry | None:
        with self._lock:
            self._evict_expired()
            entry = self._entries.get(content_hash)
            if entry is None:
                self._misses += 1
                return None
            if datetime.fromisoformat(entry.expires_at) < datetime.now(tz=UTC):
                del self._entries[content_hash]
                self._evictions += 1
                self._misses += 1
                return None
            entry.access_count += 1
            self._entries.move_to_end(content_hash)
            self._hits += 1
            return entry

    def put(self, entry: CCREntry) -> None:
        with self._lock:
            # Evict oldest if at capacity
            while len(self._entries) >= self._max:
                self._entries.popitem(last=False)
                self._evictions += 1
            self._entries[entry.content_hash] = entry

    def remove(self, content_hash: str) -> None:
        with self._lock:
            self._entries.pop(content_hash, None)

    def stats(self) -> CCRStats:
        with self._lock:
            self._evict_expired()
            return CCRStats(
                entries=len(self._entries),
                max_entries=self._max,
                ttl_seconds=self._ttl,
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
            )

    def _evict_expired(self) -> None:
        now = datetime.now(tz=UTC)
        expired = [
            k for k, e in self._entries.items() if datetime.fromisoformat(e.expires_at) < now
        ]
        for k in expired:
            del self._entries[k]
            self._evictions += 1


class SQLiteCCRBackend(CCRCacheBackend):
    """SQLite-backed CCR cache (persistent across restarts)."""

    def __init__(
        self,
        db_path: str | Path = ".storage/opencontext/ccr_cache.db",
        max_entries: int = 500,
        ttl_seconds: int = 300,
    ) -> None:
        self._path = str(db_path)
        self._max = max_entries
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._init_db()

    def _init_db(self) -> None:
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS ccr_cache (
                    content_hash TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    original TEXT NOT NULL,
                    compressed TEXT NOT NULL,
                    stored_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_ccr_expires ON ccr_cache(expires_at);
            """)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get(self, content_hash: str) -> CCREntry | None:
        self.evict_expired()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM ccr_cache WHERE content_hash = ?",
                (content_hash,),
            ).fetchone()
        if row is None:
            self._misses += 1
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.now(tz=UTC):
            self._remove(content_hash)
            self._misses += 1
            return None
        self._hits += 1
        with self._connect() as conn:
            conn.execute(
                "UPDATE ccr_cache SET access_count = access_count + 1 WHERE content_hash = ?",
                (content_hash,),
            )
        return CCREntry(
            content_hash=row["content_hash"],
            content_type=row["content_type"],
            original=row["original"],
            compressed=row["compressed"],
            stored_at=row["stored_at"],
            expires_at=row["expires_at"],
            access_count=row["access_count"],
        )

    def put(self, entry: CCREntry) -> None:
        # Evict expired + oldest if at capacity
        self.evict_expired()
        with self._connect() as conn:
            count = conn.execute("SELECT COUNT(*) as cnt FROM ccr_cache").fetchone()["cnt"]
            if count >= self._max:
                # Evict oldest accessed
                conn.execute(
                    "DELETE FROM ccr_cache WHERE content_hash IN "
                    "(SELECT content_hash FROM ccr_cache"
                    " ORDER BY access_count ASC, expires_at ASC LIMIT ?)",
                    (max(1, count - self._max + 1),),
                )
            conn.execute(
                "INSERT OR REPLACE INTO ccr_cache "
                "(content_hash, content_type, original, compressed,"
                " stored_at, expires_at, access_count) "
                "VALUES (?, ?, ?, ?, ?, ?, 0)",
                (
                    entry.content_hash,
                    entry.content_type,
                    entry.original,
                    entry.compressed,
                    entry.stored_at,
                    entry.expires_at,
                ),
            )

    def _remove(self, content_hash: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM ccr_cache WHERE content_hash = ?", (content_hash,))

    def remove(self, content_hash: str) -> None:
        self._remove(content_hash)

    def stats(self) -> CCRStats:
        self.evict_expired()
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM ccr_cache").fetchone()
            count = row["cnt"] if row else 0
        return CCRStats(
            entries=count,
            max_entries=self._max,
            ttl_seconds=self._ttl,
            hits=self._hits,
            misses=self._misses,
            evictions=self._evictions,
        )

    def evict_expired(self) -> int:
        with self._connect() as conn:
            now = datetime.now(tz=UTC).isoformat()
            cursor = conn.execute("DELETE FROM ccr_cache WHERE expires_at < ?", (now,))
            return cursor.rowcount


def store_original(
    original: str,
    compressed: str,
    *,
    backend: CCRCacheBackend,
    content_type: str = "prose",
    ttl_seconds: int = 300,
) -> str:
    """Store original content before compression.

    Args:
        original: The uncompressed content.
        compressed: The compressed version.
        backend: Cache backend (caller-owned — inject a MemoryCCRBackend
            or SQLiteCCRBackend; no module-global default).
        content_type: Type hint for the content.
        ttl_seconds: How long to keep the original.

    Returns:
        Content hash (use as retrieval token).
    """
    content_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()[:16]
    now = datetime.now(tz=UTC)
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
    entry = CCREntry(
        content_hash=content_hash,
        content_type=content_type,
        original=original,
        compressed=compressed,
        stored_at=now.isoformat(),
        expires_at=expires_at,
    )
    backend.put(entry)
    return content_hash


def retrieve_original(
    content_hash: str,
    *,
    backend: CCRCacheBackend,
) -> str | None:
    """Retrieve original content by hash.

    Args:
        content_hash: The hash returned by ``store_original``.
        backend: Cache backend (caller-owned).

    Returns:
        Original content string, or None if expired/missing.
    """
    entry = backend.get(content_hash)
    if entry is None:
        return None
    return entry.original


def compress_with_ccr(
    content: str,
    *,
    content_type: str,
    compress_fn: Any,  # Callable[[str], str]
    backend: CCRCacheBackend,
    retrieve_tool_name: str = "retrieve_original",
    ttl_seconds: int = 300,
) -> str:
    """Compress content and embed a retrieval token.

    The compressed output includes a marker the LLM can use to request
    the original: ``[CCR:<hash>]``.

    Args:
        content: Original content.
        content_type: Type hint.
        compress_fn: Function that takes str and returns compressed str.
        retrieve_tool_name: Name of the MCP/tool for retrieval.
        backend: Cache backend.
        ttl_seconds: TTL for cached original.

    Returns:
        Compressed content with embedded CCR token.
    """
    compressed: str = compress_fn(content)
    content_hash = store_original(
        content,
        compressed,
        content_type=content_type,
        backend=backend,
        ttl_seconds=ttl_seconds,
    )
    # Append retrieval instruction as a compact marker
    marker = f"\n[CCR:{content_hash}]"
    return compressed + marker


def ccr_stats(*, backend: CCRCacheBackend) -> CCRStats:
    """Get cache statistics."""
    return backend.stats()


__all__ = [
    "CCRCacheBackend",
    "CCREntry",
    "CCRStats",
    "MemoryCCRBackend",
    "SQLiteCCRBackend",
    "ccr_stats",
    "compress_with_ccr",
    "retrieve_original",
    "store_original",
]
