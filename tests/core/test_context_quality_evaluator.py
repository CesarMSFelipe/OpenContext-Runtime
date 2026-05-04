from __future__ import annotations

from opencontext_core.evaluation import (
    ContextBenchCase,
    ContextBenchEvaluator,
    ContextQualityEvaluator,
)
from opencontext_core.models.context import ContextPackResult
from opencontext_core.runtime import OpenContextRuntime


def test_context_quality_evaluator_reports_high_risk_without_sources() -> None:
    report = ContextQualityEvaluator().evaluate_pack(
        ContextPackResult(
            included=[],
            omitted=[],
            used_tokens=0,
            available_tokens=100,
            omissions=[],
        )
    )

    assert report.quality_risk == "high"
    assert "missing_sources" in report.warnings


def test_context_quality_evaluator_flags_over_budget() -> None:
    report = ContextQualityEvaluator().evaluate_pack(
        ContextPackResult(
            included=[],
            omitted=[],
            used_tokens=101,
            available_tokens=100,
            omissions=[],
        )
    )

    assert report.quality_risk == "high"
    assert "over_budget" in report.warnings


def test_contextbench_evaluator_checks_expected_sources(tmp_path) -> None:
    source = tmp_path / "auth.py"
    source.write_text(
        "def authenticate_user(token: str) -> bool:\n    return token == 'test-token'\n",
        encoding="utf-8",
    )
    (tmp_path / "billing.py").write_text("def invoice() -> None:\n    pass\n", encoding="utf-8")

    runtime = OpenContextRuntime(storage_path=tmp_path / ".storage" / "opencontext")
    runtime.index_project(tmp_path)

    result = ContextBenchEvaluator(
        runtime,
        root=tmp_path,
        max_tokens=1000,
        min_token_reduction=0.0,
    ).evaluate_suite(
        [
            ContextBenchCase(
                id="auth-source",
                query="Where is authenticate_user implemented?",
                expected_sources=["auth.py"],
                forbidden_sources=["missing.py"],
            )
        ]
    )

    assert result.passed
    assert result.cases[0].source_coverage == 1.0
