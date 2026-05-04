from __future__ import annotations

from opencontext_core.memory_usability import OutputBudgetController, OutputMode


def test_output_mode_resolves_and_budget_reports() -> None:
    result = OutputBudgetController(max_output_tokens=6).apply(
        "one two three four five six seven eight",
        mode="concise",
    )

    assert result.mode is OutputMode.CONCISE
    assert result.truncated is True
    assert result.final_tokens <= result.max_output_tokens + 8


def test_technical_terse_preserves_paths_symbols_numbers() -> None:
    content = "Please carefully review src/auth.py where AccessResolver failed 403."
    result = OutputBudgetController().apply(content, mode=OutputMode.TECHNICAL_TERSE)

    assert "src/auth.py" in result.content
    assert "AccessResolver" in result.content
    assert "403" in result.content


def test_patch_only_omits_long_explanation() -> None:
    content = "Long explanation\n--- a/app.py\n+++ b/app.py\n@@\n-old\n+new\n"

    result = OutputBudgetController().apply(content, mode=OutputMode.PATCH_ONLY)

    assert "Long explanation" not in result.content
    assert "+new" in result.content
