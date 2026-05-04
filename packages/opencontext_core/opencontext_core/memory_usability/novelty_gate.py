"""Novelty and retention quality gate for harvested memory."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.memory_usability.memory_candidates import MemoryCandidate
from opencontext_core.models.context import DataClassification


class NoveltyDecision(BaseModel):
    """Decision from the memory novelty gate."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool = Field(description="Whether the candidate should be stored.")
    reason: str = Field(description="Stable decision reason.")
    score: float = Field(ge=0.0, le=1.0, description="Composite utility score.")


class NoveltyGate:
    """Rejects duplicate, trivial, stale, or risky memory candidates."""

    def __init__(self, min_score: float = 0.45, max_tokens: int = 400) -> None:
        self.min_score = min_score
        self.max_tokens = max_tokens

    def evaluate(
        self,
        candidate: MemoryCandidate,
        existing_contents: list[str] | None = None,
    ) -> NoveltyDecision:
        """Evaluate a memory candidate against simple deterministic criteria."""

        existing = {content.strip().lower() for content in existing_contents or []}
        normalized = candidate.content.strip().lower()
        if not candidate.source:
            return NoveltyDecision(accepted=False, reason="missing_source", score=0.0)
        if len(normalized.split()) < 4:
            return NoveltyDecision(accepted=False, reason="trivial_candidate", score=0.0)
        if normalized in existing:
            return NoveltyDecision(accepted=False, reason="duplicate", score=0.0)
        if candidate.classification in {DataClassification.SECRET, DataClassification.REGULATED}:
            return NoveltyDecision(accepted=False, reason="classification_too_sensitive", score=0.0)
        if candidate.token_cost > self.max_tokens:
            return NoveltyDecision(accepted=False, reason="too_large_for_value", score=0.2)
        risk_penalty = 0.15 if candidate.classification is DataClassification.CONFIDENTIAL else 0.0
        score = max(
            0.0,
            min(
                1.0,
                candidate.novelty_score * 0.35
                + candidate.reuse_likelihood * 0.35
                + candidate.source_trust * 0.2
                + (1.0 - min(candidate.token_cost / max(self.max_tokens, 1), 1.0)) * 0.1
                - risk_penalty,
            ),
        )
        return NoveltyDecision(
            accepted=score >= self.min_score,
            reason="accepted" if score >= self.min_score else "low_utility",
            score=score,
        )
