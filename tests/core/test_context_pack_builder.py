from __future__ import annotations

from opencontext_core.context.packing import ContextPackBuilder
from opencontext_core.models.context import ContextItem, ContextPriority


def _item(
    item_id: str,
    priority: ContextPriority,
    tokens: int,
    score: float,
    source_type: str = "file",
) -> ContextItem:
    return ContextItem(
        id=item_id,
        content=item_id,
        source=f"{item_id}.py",
        source_type=source_type,
        priority=priority,
        tokens=tokens,
        score=score,
    )


def test_context_pack_includes_required_context_and_enforces_budget() -> None:
    result = ContextPackBuilder().pack(
        [
            _item("required", ContextPriority.P1, 30, 0.7),
            _item("large-low-value", ContextPriority.P5, 100, 0.2),
            _item("supporting", ContextPriority.P2, 25, 0.8),
        ],
        available_tokens=60,
        required_priorities={ContextPriority.P0, ContextPriority.P1},
    )

    assert [item.id for item in result.included] == ["required", "supporting"]
    assert result.used_tokens == 55
    assert result.omissions[0].item_id == "large-low-value"
    assert result.omissions[0].reason == "item_exceeds_available_budget"


def test_context_pack_value_per_token_ordering() -> None:
    result = ContextPackBuilder().pack(
        [
            _item("dense", ContextPriority.P2, 10, 0.7),
            _item("large", ContextPriority.P2, 100, 0.9),
            _item("priority", ContextPriority.P1, 10, 0.1),
        ],
        available_tokens=30,
    )

    assert [item.id for item in result.included] == ["priority", "dense"]
    assert result.omitted[0].metadata["context_pack"]["decision"] == "item_exceeds_available_budget"
