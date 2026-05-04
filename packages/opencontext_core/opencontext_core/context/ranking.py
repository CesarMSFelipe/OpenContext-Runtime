"""Deterministic context ranking."""

from __future__ import annotations

from datetime import datetime

from opencontext_core.compat import UTC
from opencontext_core.config import RankingWeightsConfig
from opencontext_core.models.context import ContextItem

SOURCE_TRUST: dict[str, float] = {
    "system": 1.0,
    "project_manifest": 0.9,
    "symbol": 0.85,
    "file": 0.8,
    "memory": 0.75,
    "conversation": 0.65,
    "tool": 0.6,
}


class ContextRanker:
    """Ranks context with a documented deterministic weighted formula."""

    def __init__(self, weights: RankingWeightsConfig) -> None:
        self.weights = weights

    def rank(self, items: list[ContextItem]) -> list[ContextItem]:
        """Return ranked copies of context items in descending score order."""

        ranked = [self._score_item(item) for item in items]
        return sorted(
            ranked,
            key=lambda item: (-item.score, int(item.priority), item.tokens, item.id),
        )

    def _score_item(self, item: ContextItem) -> ContextItem:
        retrieval_relevance = max(0.0, min(1.0, item.score))
        priority_score = (5 - int(item.priority)) / 5
        source_trust = SOURCE_TRUST.get(item.source_type, 0.5)
        token_efficiency = 1 / (1 + (item.tokens / 1000))
        recency_bonus = _recency_bonus(item)
        score = (
            self.weights.relevance * retrieval_relevance
            + self.weights.priority * priority_score
            + self.weights.source_trust * source_trust
            + self.weights.token_efficiency * token_efficiency
            + recency_bonus
        )
        metadata = dict(item.metadata)
        metadata["ranking"] = {
            "retrieval_relevance": retrieval_relevance,
            "priority_score": priority_score,
            "source_trust": source_trust,
            "token_efficiency": token_efficiency,
            "recency_bonus": recency_bonus,
            "formula": (
                "relevance*w + priority*w + source_trust*w + token_efficiency*w + recency_bonus"
            ),
        }
        return item.model_copy(update={"score": round(score, 6), "metadata": metadata})


def _recency_bonus(item: ContextItem) -> float:
    raw_modified_at = item.metadata.get("modified_at")
    if not isinstance(raw_modified_at, str):
        return 0.0
    try:
        modified_at = datetime.fromisoformat(raw_modified_at)
    except ValueError:
        return 0.0
    if modified_at.tzinfo is None:
        modified_at = modified_at.replace(tzinfo=UTC)
    age_days = max(0, (datetime.now(tz=UTC) - modified_at.astimezone(UTC)).days)
    if age_days <= 7:
        return 0.05
    if age_days <= 30:
        return 0.03
    if age_days <= 180:
        return 0.01
    return 0.0
