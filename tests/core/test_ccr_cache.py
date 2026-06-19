"""Tests for CCR Cache — reversible compression cache."""

from __future__ import annotations

from opencontext_core.compression.ccr_cache import (
    MemoryCCRBackend,
    compress_with_ccr,
    retrieve_original,
    store_original,
)


def _make_backend() -> MemoryCCRBackend:
    return MemoryCCRBackend(max_entries=10, ttl_seconds=60)


def test_store_and_retrieve_roundtrip() -> None:
    backend = _make_backend()
    content_hash = store_original("original text", "compressed", backend=backend)
    recovered = retrieve_original(content_hash, backend=backend)
    assert recovered == "original text"


def test_retrieve_missing_returns_none() -> None:
    backend = _make_backend()
    assert retrieve_original("nonexistent-hash", backend=backend) is None


def test_compress_with_ccr_embeds_token() -> None:
    backend = _make_backend()
    result = compress_with_ccr(
        "some long content",
        content_type="prose",
        compress_fn=lambda s: s[:5],
        backend=backend,
    )
    assert "[CCR:" in result
    assert result.startswith("some ")


def test_eviction_at_capacity() -> None:
    backend = MemoryCCRBackend(max_entries=2, ttl_seconds=60)
    store_original("a", "ca", backend=backend)
    store_original("b", "cb", backend=backend)
    store_original("c", "cc", backend=backend)  # evicts the oldest ("a")
    stats = backend.stats()
    assert stats.entries == 2
    assert stats.evictions >= 1


def test_stats_tracks_hits_and_misses() -> None:
    backend = _make_backend()
    h = store_original("content", "comp", backend=backend)
    retrieve_original(h, backend=backend)  # hit
    retrieve_original("bad-hash", backend=backend)  # miss
    s = backend.stats()
    assert s.hits == 1
    assert s.misses == 1
