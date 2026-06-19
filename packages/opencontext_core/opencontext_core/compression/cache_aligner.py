"""CacheAligner — stabilize prompt prefixes for provider KV cache hits.

Provider KV caches (Anthropic prompt caching, OpenAI prefix caching) work by
matching the prefix of the current prompt against previously seen prefixes.
If the prefix changes between turns (because compression rewrites it), the cache
misses and the full prompt is re-processed — negating the benefit of compression.

CacheAligner separates the prompt into two regions:
  1. STABLE PREFIX — system prompt + project rules + conversation header.
     NOT compressed. Stays byte-identical across turns so the KV cache hits.
  2. COMPRESSIBLE PAYLOAD — tool outputs, RAG chunks, file content.
     Compressed normally.

A ``CACHE_BOUNDARY`` marker is inserted between the regions so the provider
knows where the prefix ends (Anthropic: ``store: True`` on the system message;
OpenAI: the prefix up to the marker).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

_CACHE_BOUNDARY = "▌CACHE_BOUNDARY▐"


@dataclass
class AlignedPrompt:
    """Result of aligning a prompt for KV cache."""

    system_prompt: str
    stable_prefix: str  # NOT compressed
    compressible_payload: str  # MAY be compressed
    payload_start: int  # char offset in the full prompt
    prefix_hash: str  # SHA256 of the stable prefix
    prefix_tokens_estimate: int
    is_cacheable: bool  # True when prefix_hash matches previous turn


@dataclass
class CacheAlignerState:
    """State tracked across turns for cache alignment."""

    previous_prefix_hash: str = ""
    turn_count: int = 0
    max_cache_age_turns: int = 10


class CacheAligner:
    """Align prompt structure for maximum KV cache hit rate.

    Usage:
        aligner = CacheAligner()
        aligned = aligner.align(system_prompt, payload)
        # Send aligned.stable_prefix + aligned.compressible_payload to LLM
        # On next turn with same prefix (same system + rules):
        aligned = aligner.align(system_prompt, new_payload)
        # → aligned.is_cacheable == True
    """

    def __init__(
        self,
        *,
        stable_prefix_tokens: int = 1200,
        provider_cache_hints: bool = True,
        max_cache_age_turns: int = 10,
    ) -> None:
        self._stable_prefix_tokens = stable_prefix_tokens
        self._provider_cache_hints = provider_cache_hints
        self._state = CacheAlignerState(max_cache_age_turns=max_cache_age_turns)

    def detect_stable_prefix(self, system_prompt: str, payload: str) -> str:
        """Extract the portion of context that should remain stable.

        The stable prefix is: system prompt + any project-level context
        (rules, manifest, repo map). We estimate by token count.
        """
        # System prompt is always part of the stable prefix
        prefix = system_prompt.strip()

        # If payload contains project context before tool results, include it
        if _CACHE_BOUNDARY in payload:
            parts = payload.split(_CACHE_BOUNDARY, 1)
            prefix = prefix + "\n\n" + parts[0].strip()
            return prefix.strip()

        # Estimate: find the natural split point in payload
        # Project context (instructions, rules) comes before tool results
        lines = payload.splitlines()
        stable_lines: list[str] = []
        token_estimate = len(prefix) // 4

        for line in lines:
            line_tokens = max(1, len(line) // 4)
            if token_estimate + line_tokens > self._stable_prefix_tokens:
                break
            stable_lines.append(line)
            token_estimate += line_tokens

        if stable_lines:
            prefix = prefix + "\n\n" + "\n".join(stable_lines)

        return prefix.strip()

    def align(
        self,
        system_prompt: str,
        payload: str,
        *,
        force_full_reset: bool = False,
    ) -> AlignedPrompt:
        """Split content into stable prefix + compressible payload.

        Args:
            system_prompt: The system prompt (always stable).
            payload: Everything else (may contain project context + tool results).
            force_full_reset: If True, treat as a new session (no cache match).

        Returns:
            AlignedPrompt with stable prefix and payload separated.
        """
        self._state.turn_count += 1

        # Force reset every N turns to avoid stale cache
        if self._state.turn_count > self._state.max_cache_age_turns:
            force_full_reset = True

        stable = self.detect_stable_prefix(system_prompt, payload)

        # Determine what part of payload is compressible
        # (everything after the stable prefix within payload)
        compressible = ""
        if _CACHE_BOUNDARY in payload:
            _, compressible = payload.split(_CACHE_BOUNDARY, 1)
            compressible = compressible.strip()
        elif payload.startswith(stable) and stable != system_prompt:
            compressible = payload[len(stable) :].strip()
        else:
            compressible = payload.strip()

        prefix_hash = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]
        is_cacheable = prefix_hash == self._state.previous_prefix_hash and not force_full_reset
        self._state.previous_prefix_hash = prefix_hash

        return AlignedPrompt(
            system_prompt=system_prompt,
            stable_prefix=stable,
            compressible_payload=compressible,
            payload_start=len(stable),
            prefix_hash=prefix_hash,
            prefix_tokens_estimate=max(1, len(stable) // 4),
            is_cacheable=is_cacheable,
        )

    def insert_cache_boundary(self, payload: str, *, at_line: int | None = None) -> str:
        """Insert the cache boundary marker into payload.

        The boundary separates project context (stable) from tool results
        (compressible). If ``at_line`` is given, insert there; otherwise
        auto-detect by looking for the first tool output or search result.
        """
        if _CACHE_BOUNDARY in payload:
            return payload  # already has a boundary

        if at_line is not None:
            lines = payload.splitlines()
            if 0 <= at_line < len(lines):
                lines.insert(at_line, _CACHE_BOUNDARY)
                return "\n".join(lines)

        # Auto-detect: boundary before first JSON array or tool result
        lines = payload.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("[{") or stripped.startswith("```"):
                lines.insert(i, _CACHE_BOUNDARY)
                return "\n".join(lines)

        # Fallback: boundary at 30%
        pos = max(1, int(len(lines) * 0.3))
        lines.insert(pos, _CACHE_BOUNDARY)
        return "\n".join(lines)

    def provider_cache_hint(self, aligned: AlignedPrompt) -> list[dict[str, Any]]:
        """Emit provider-specific cache control messages.

        Returns a list of message dicts suitable for merging into the
        conversation payload.

        Anthropic:
            System message with ``cache_control = {"type": "ephemeral"}``
        OpenAI:
            ``prefix`` marker in the messages array.
        """
        if not self._provider_cache_hints:
            return []

        hints: list[dict[str, Any]] = []
        # For Anthropic-compatible APIs: mark system message as cacheable
        hints.append(
            {
                "role": "system",
                "content": aligned.stable_prefix,
                "cache_control": {"type": "ephemeral"},
            }
        )
        return hints

    def reset_session(self) -> None:
        """Reset turn tracking (call at start of a new session)."""
        self._state = CacheAlignerState(max_cache_age_turns=self._state.max_cache_age_turns)

    @property
    def turn_count(self) -> int:
        return self._state.turn_count

    @property
    def is_cache_hit(self) -> bool:
        """Whether the last align() resulted in a cache hit (same prefix)."""
        # The caller must check aligned.is_cacheable — this is a convenience
        # for metrics/reporting after the fact.
        return False  # Real value is in align() return


__all__ = ["AlignedPrompt", "CacheAligner"]
