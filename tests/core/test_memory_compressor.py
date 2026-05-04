from __future__ import annotations

from opencontext_core.memory_usability import MemoryCandidate, MemoryCompressor, MemoryKind
from opencontext_core.models.context import DataClassification


def test_memory_compressor_preserves_expansion_ref() -> None:
    candidate = MemoryCandidate(
        content=" ".join(["AccessResolver"] * 200),
        source="trace:abc",
        kind=MemoryKind.SUMMARY,
        novelty_score=0.8,
        reuse_likelihood=0.8,
        classification=DataClassification.INTERNAL,
        token_cost=200,
    )

    compressed = MemoryCompressor().compress(candidate, max_tokens=20)

    assert compressed.source_ref == "trace:abc"
    assert "[EXPAND:trace:abc]" in compressed.content
