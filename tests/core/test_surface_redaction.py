from __future__ import annotations

from dataclasses import dataclass

from opencontext_cli.main import _ask
from opencontext_core.models.context import (
    ContextItem,
    ContextOmission,
    ContextPackResult,
    ContextPriority,
    DataClassification,
)


@dataclass
class _AskResult:
    answer: str
    trace_id: str
    token_usage: dict[str, int]
    selected_context_count: int


class _FakeRuntime:
    def ask(self, _question: str) -> _AskResult:
        return _AskResult(
            answer="email admin@example.com and sk-abcdefghijklmnopqrstuvwxyz123456",
            trace_id="r1",
            token_usage={"prompt": 1},
            selected_context_count=1,
        )


def test_cli_ask_redacts_sensitive_output(capsys) -> None:
    _ask(_FakeRuntime(), "test")
    out = capsys.readouterr().out
    assert "admin@example.com" not in out
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in out


def test_context_pack_model_can_hold_classification_metadata() -> None:
    item = ContextItem(
        id="i1",
        content="data",
        source="a.py",
        source_type="file",
        priority=ContextPriority.P2,
        tokens=1,
        score=0.1,
        classification=DataClassification.INTERNAL,
        metadata={"redacted": True},
    )
    pack = ContextPackResult(
        included=[item],
        omitted=[],
        used_tokens=1,
        available_tokens=100,
        omissions=[ContextOmission(item_id="x", reason="overflow", tokens=1, score=0.1)],
    )
    assert pack.included[0].metadata["redacted"] is True
