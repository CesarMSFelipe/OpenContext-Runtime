from __future__ import annotations

from opencontext_core.context.adaptive_compression import AdaptiveCompressionController
from opencontext_core.models.context import CompressionStrategy, ContextPriority


def test_high_risk_task_avoids_lossy_compression() -> None:
    decision = AdaptiveCompressionController().decide(
        query_complexity=0.8,
        retrieval_confidence=0.9,
        task_risk="security",
        source_type="file",
        token_pressure=0.9,
        priority=ContextPriority.P4,
    )

    assert decision.strategy is CompressionStrategy.NONE
    assert decision.allow_lossy is False


def test_code_prefers_extractive_and_high_pressure_increases_compression() -> None:
    controller = AdaptiveCompressionController()
    code_decision = controller.decide(
        query_complexity=0.5,
        retrieval_confidence=0.9,
        task_risk="low",
        source_type="code",
        token_pressure=0.5,
        priority=ContextPriority.P3,
    )
    pressure_decision = controller.decide(
        query_complexity=0.5,
        retrieval_confidence=0.9,
        task_risk="low",
        source_type="memory",
        token_pressure=0.9,
        priority=ContextPriority.P5,
    )

    assert code_decision.strategy is CompressionStrategy.EXTRACTIVE_HEAD_TAIL
    assert pressure_decision.max_ratio < code_decision.max_ratio


def test_p0_p1_protected_behavior() -> None:
    decision = AdaptiveCompressionController().decide(
        query_complexity=0.1,
        retrieval_confidence=1.0,
        task_risk="low",
        source_type="file",
        token_pressure=0.9,
        priority=ContextPriority.P1,
    )

    assert decision.strategy is CompressionStrategy.NONE
    assert decision.allow_lossy is False
