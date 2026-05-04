"""Memory compression helpers with source expansion references."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.memory_usability.memory_candidates import MemoryCandidate
from opencontext_core.safety.redaction import SinkGuard


class CompressedMemory(BaseModel):
    """Compressed memory with expansion provenance."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(description="Compressed redacted content.")
    original_tokens: int = Field(ge=0, description="Original token estimate.")
    compressed_tokens: int = Field(ge=0, description="Compressed token estimate.")
    source_ref: str = Field(description="Expansion source reference.")
    reversible: bool = Field(description="Whether exact reconstruction is available.")


class MemoryCompressor:
    """Compresses memory facts conservatively."""

    def compress(self, candidate: MemoryCandidate, *, max_tokens: int = 120) -> CompressedMemory:
        """Compress a candidate while preserving source references."""

        safe = SinkGuard().redact(candidate.content)[0]
        original_tokens = estimate_tokens(safe)
        content = safe
        if original_tokens > max_tokens:
            words = safe.split()
            content = " ".join(words[: max(1, max_tokens * 2)])
            content = f"{content} [EXPAND:{candidate.source}]"
        return CompressedMemory(
            content=content,
            original_tokens=original_tokens,
            compressed_tokens=estimate_tokens(content),
            source_ref=candidate.source,
            reversible=False,
        )
