"""Memory forbidden-content rule (SPEC MEM-1).

In addition to the existing secret redaction (``SinkGuard``) and classification
gate (``novelty_gate``), memory write candidates MUST be rejected when they carry
chain-of-thought reasoning or raw private logs. This is a deterministic marker
scan, reused by both the candidate gate (``novelty_gate``) and the persistence
chokepoint (``memory/graph.py``).
"""

from __future__ import annotations

# Markers of chain-of-thought / raw reasoning that must never be persisted.
_CHAIN_OF_THOUGHT_MARKERS = (
    "<thinking>",
    "</thinking>",
    "chain of thought",
    "chain-of-thought",
    "let me think",
    "let's think step by step",
    "step by step reasoning",
    "reasoning:",
    "my reasoning is",
    "thinking out loud",
    "first, i'll",
    "first, i will",
)

# Markers of raw private logs / dumps.
_RAW_LOG_MARKERS = (
    "traceback (most recent call last)",
    "debug log:",
    "raw log:",
    "stdout dump",
    "-----begin",
)


def forbidden_memory_content(text: str) -> str | None:
    """Return a stable reason if *text* is forbidden for memory, else ``None``.

    Conservative: matches explicit chain-of-thought / raw-log markers so distilled
    facts and decisions (the legitimate memory payload) are never rejected.
    """
    normalized = text.strip().lower()
    if not normalized:
        return None
    for marker in _CHAIN_OF_THOUGHT_MARKERS:
        if marker in normalized:
            return "chain_of_thought_excluded"
    for marker in _RAW_LOG_MARKERS:
        if marker in normalized:
            return "raw_private_log_excluded"
    return None
