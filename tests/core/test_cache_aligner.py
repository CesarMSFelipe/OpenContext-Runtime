"""Tests for CacheAligner — KV cache-aware prompt splitting."""

from __future__ import annotations

from opencontext_core.compression.cache_aligner import CacheAligner

_SYSTEM = "You are a helpful assistant. Follow these rules exactly."
_PAYLOAD = "User file content:\n```\nsome code here\n```"


def test_align_splits_into_stable_and_compressible() -> None:
    aligner = CacheAligner(stable_prefix_tokens=20)
    aligned = aligner.align(_SYSTEM, _PAYLOAD)
    assert aligned.system_prompt == _SYSTEM
    assert aligned.stable_prefix != ""
    assert aligned.prefix_hash != ""


def test_second_turn_same_system_is_cacheable() -> None:
    # Stable prefix includes system + payload lines up to token budget.
    # Using the same payload twice keeps the prefix hash identical.
    aligner = CacheAligner(stable_prefix_tokens=200)
    aligner.align(_SYSTEM, _PAYLOAD)
    aligned2 = aligner.align(_SYSTEM, _PAYLOAD)
    assert aligned2.is_cacheable is True


def test_different_system_not_cacheable() -> None:
    aligner = CacheAligner(stable_prefix_tokens=200)
    aligner.align(_SYSTEM, _PAYLOAD)
    aligned2 = aligner.align("completely different system prompt", _PAYLOAD)
    assert aligned2.is_cacheable is False


def test_insert_cache_boundary_at_line() -> None:
    aligner = CacheAligner()
    payload = "line0\nline1\nline2"
    result = aligner.insert_cache_boundary(payload, at_line=1)
    assert "▌CACHE_BOUNDARY▐" in result
    lines = result.splitlines()
    boundary_idx = next(i for i, line in enumerate(lines) if "CACHE_BOUNDARY" in line)
    assert boundary_idx == 1


def test_force_reset_breaks_cache_match() -> None:
    aligner = CacheAligner(stable_prefix_tokens=200)
    aligner.align(_SYSTEM, _PAYLOAD)
    aligned2 = aligner.align(_SYSTEM, _PAYLOAD, force_full_reset=True)
    assert aligned2.is_cacheable is False
