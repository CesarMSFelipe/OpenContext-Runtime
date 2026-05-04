from __future__ import annotations

from pathlib import Path

from opencontext_core.evaluation import BasicEvaluator, EvalCase, load_eval_cases


def test_loading_eval_cases_and_basic_result(tmp_path: Path) -> None:
    path = tmp_path / "eval.yaml"
    path.write_text(
        "cases:\n"
        "  - id: auth\n"
        "    workflow: code_assistant\n"
        "    input: Where is auth?\n"
        "    expected_sources: [src/auth.py]\n",
        encoding="utf-8",
    )

    cases = load_eval_cases(path)
    result = BasicEvaluator().evaluate(cases[0])

    assert cases[0] == EvalCase(
        id="auth",
        workflow="code_assistant",
        input="Where is auth?",
        expected_sources=["src/auth.py"],
    )
    assert result.passed is True
    assert result.score == 1.0
