"""Doctor's capability-graph check reports real capabilities on a source-only repo.

Regression: a clean python project with a test file but no pyproject.toml/pytest.ini
reported ``capabilities.graph: 0/2 ready — none`` because detection was manifest-gated.
It must now surface the genuine python/pytest/git capabilities.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from opencontext_core.doctor.checks import _check_capability_graph


def test_capability_graph_check_passes_on_source_only_python_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_add():\n    assert True\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)

    check = _check_capability_graph()

    assert check.name == "capabilities.graph"
    assert check.ok is True
    # Honest, meaningful counts — not "0/2 ready — none".
    assert "0/" not in check.details
    assert "none" not in check.details
    for capability in ("python", "pytest", "git"):
        assert capability in check.details
