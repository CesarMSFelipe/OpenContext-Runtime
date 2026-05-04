from __future__ import annotations

from opencontext_core.memory_usability import MemoryCandidate, MemoryKind, NoveltyGate
from opencontext_core.models.context import DataClassification


def test_novelty_gate_rejects_duplicates_and_sensitive_candidates() -> None:
    candidate = MemoryCandidate(
        content="Access control is centralized in AccessResolver.",
        source="trace:abc",
        kind=MemoryKind.FACT,
        novelty_score=0.9,
        reuse_likelihood=0.8,
        classification=DataClassification.INTERNAL,
        token_cost=10,
    )

    assert NoveltyGate().evaluate(candidate, [candidate.content]).reason == "duplicate"
    sensitive = candidate.model_copy(update={"classification": DataClassification.SECRET})
    assert NoveltyGate().evaluate(sensitive).reason == "classification_too_sensitive"
