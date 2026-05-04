from __future__ import annotations

from opencontext_core.operating_model import PreLLMQualityGate


def test_pre_llm_quality_gate_blocks_provider_policy() -> None:
    report = PreLLMQualityGate().evaluate(
        context_tokens=10,
        max_tokens=100,
        provider_allowed=False,
        source_count=1,
    )

    assert report.passed is False
    assert "provider_blocked" in report.risks
