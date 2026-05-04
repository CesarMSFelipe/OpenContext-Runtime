from __future__ import annotations

from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.ranking import ContextRanker
from opencontext_core.models.context import ContextItem, ContextPriority


def test_context_ranking_orders_by_weighted_signal() -> None:
    config = OpenContextConfig.model_validate(default_config_data())
    ranker = ContextRanker(config.context.ranking.weights)
    items = [
        ContextItem(
            id="optional-large",
            content="optional",
            source="docs/old.md",
            source_type="file",
            priority=ContextPriority.P5,
            tokens=5000,
            score=0.9,
        ),
        ContextItem(
            id="core-auth",
            content="auth implementation",
            source="src/auth.py",
            source_type="symbol",
            priority=ContextPriority.P1,
            tokens=100,
            score=0.8,
        ),
    ]

    ranked = ranker.rank(items)

    assert [item.id for item in ranked] == ["core-auth", "optional-large"]
    assert "ranking" in ranked[0].metadata
