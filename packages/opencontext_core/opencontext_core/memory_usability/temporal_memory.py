"""Temporal memory graph scaffolding."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.context import DataClassification


class TemporalFact(BaseModel):
    """Time-bounded memory fact."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Fact identifier.")
    subject: str = Field(description="Fact subject.")
    predicate: str = Field(description="Fact predicate.")
    object: str = Field(description="Fact object.")
    valid_from: datetime = Field(description="Validity start.")
    valid_until: datetime | None = Field(default=None, description="Optional validity end.")
    superseded_by: str | None = Field(default=None, description="Replacement fact id.")
    source_id: str = Field(description="Source trace or memory id.")
    confidence: float = Field(ge=0.0, le=1.0, description="Fact confidence.")
    classification: DataClassification = Field(description="Fact classification.")


class TemporalMemoryGraph:
    """In-memory temporal fact index with supersession support."""

    def __init__(self, facts: list[TemporalFact] | None = None) -> None:
        self._facts = {fact.id: fact for fact in facts or []}

    def add(self, fact: TemporalFact) -> None:
        """Add or replace one fact."""

        self._facts[fact.id] = fact

    def active_facts(self, at: datetime) -> list[TemporalFact]:
        """Return facts active at a point in time."""

        return [
            fact
            for fact in self._facts.values()
            if fact.valid_from <= at
            and (fact.valid_until is None or fact.valid_until > at)
            and fact.superseded_by is None
        ]

    def timeline(self, subject: str) -> list[TemporalFact]:
        """Return a subject timeline."""

        return sorted(
            [fact for fact in self._facts.values() if subject.lower() in fact.subject.lower()],
            key=lambda fact: fact.valid_from,
        )

    def supersede(self, fact_id: str, new_fact_id: str) -> TemporalFact:
        """Mark one fact as superseded by another."""

        fact = self._facts[fact_id]
        updated = fact.model_copy(update={"superseded_by": new_fact_id})
        self._facts[fact_id] = updated
        return updated
