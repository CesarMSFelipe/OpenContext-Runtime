from __future__ import annotations

from opencontext_core.memory_usability import OutputBudgetController


def test_output_modes_preserve_warnings() -> None:
    rendered = OutputBudgetController().apply(
        "warning: provider blocked for confidential data",
        mode="technical_terse",
    )

    assert "warning" in rendered.content
    assert "blocked" in rendered.content
