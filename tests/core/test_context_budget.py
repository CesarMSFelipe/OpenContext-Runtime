from __future__ import annotations

from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.budgeting import TokenBudgetManager, estimate_tokens
from opencontext_core.context.compression import CompressionEngine
from opencontext_core.models.context import ContextItem, ContextPriority


def _config() -> OpenContextConfig:
    return OpenContextConfig.model_validate(default_config_data())


def test_token_budget_calculation_and_selection() -> None:
    config = _config()
    manager = TokenBudgetManager(config.context)
    budget = manager.calculate()
    items = [
        ContextItem(
            id="a",
            content="a",
            source="a.py",
            source_type="file",
            priority=ContextPriority.P1,
            tokens=5000,
            score=1.0,
        ),
        ContextItem(
            id="b",
            content="b",
            source="b.py",
            source_type="file",
            priority=ContextPriority.P1,
            tokens=2000,
            score=0.9,
        ),
    ]

    selected, discarded = manager.select_within_budget(items)

    assert budget.available_context_tokens == 10500
    assert manager.budget_for_section("retrieved_context") == 6500
    assert [item.id for item in selected] == ["a"]
    assert discarded[0].metadata["discard_reason"] == "token_budget_exceeded"


def test_compression_respects_budget() -> None:
    config = _config()
    engine = CompressionEngine(config.context.compression)
    content = "authentication " * 80
    items = [
        ContextItem(
            id=str(index),
            content=content,
            source=f"{index}.py",
            source_type="file",
            priority=ContextPriority.P1,
            tokens=estimate_tokens(content),
            score=1.0,
        )
        for index in range(2)
    ]

    compressed, results = engine.compress_items(items, budget_tokens=120)

    assert sum(item.tokens for item in compressed) <= 120
    assert results[0].compressed_tokens <= results[0].original_tokens
    assert compressed[0].metadata["compression"]["strategy"] == "extractive_head_tail"
