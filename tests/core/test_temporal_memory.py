from __future__ import annotations

from datetime import datetime

from opencontext_core.compat import UTC
from opencontext_core.memory_usability import TemporalFact, TemporalMemoryGraph
from opencontext_core.models.context import DataClassification


def test_temporal_memory_filters_superseded_facts() -> None:
    now = datetime.now(tz=UTC)
    fact = TemporalFact(
        id="fact-1",
        subject="access control",
        predicate="uses",
        object="AccessResolver",
        valid_from=now,
        source_id="trace:abc",
        confidence=0.8,
        classification=DataClassification.INTERNAL,
    )
    graph = TemporalMemoryGraph([fact])
    graph.supersede("fact-1", "fact-2")

    assert graph.active_facts(now) == []
