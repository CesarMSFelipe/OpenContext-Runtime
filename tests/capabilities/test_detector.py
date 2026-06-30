"""build_capability_graph reuses existing detection without duplicating it (CP-004)."""

from __future__ import annotations

from pathlib import Path

from opencontext_core.capabilities.detector import STRICT_HARNESS, build_capability_graph
from opencontext_core.sdd_runtime import detect_test_capabilities


def _node_ids(root: Path) -> set[str]:
    return {n.id for n in build_capability_graph(root).nodes}


def test_python_project_yields_pytest_and_ruff_with_evidence(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    graph = build_capability_graph(tmp_path)
    by_id = {n.id: n for n in graph.nodes}

    assert "pytest" in by_id
    assert "ruff-check" in by_id
    assert by_id["pytest"].available is True
    assert by_id["pytest"].evidence != ""
    assert by_id["pytest"].kind == "test"
    assert by_id["ruff-check"].kind == "lint"


def test_empty_project_yields_no_test_or_lint_nodes_and_does_not_raise(tmp_path: Path) -> None:
    graph = build_capability_graph(tmp_path)

    test_lint = [n for n in graph.nodes if n.kind in {"test", "lint", "type"}]
    assert test_lint == []  # no tooling markers -> no tooling nodes


def test_detector_reuses_detect_test_capabilities_one_to_one(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "go.mod").write_text("module x\n", encoding="utf-8")

    detected = {c.name: c for c in detect_test_capabilities(tmp_path)}
    by_id = {n.id: n for n in build_capability_graph(tmp_path).nodes}

    # Every detected tooling capability appears as a node with identical evidence
    # (the detector lifts the existing facts, it does not re-detect them).
    for name, cap in detected.items():
        assert name in by_id, f"detector dropped {name}"
        assert by_id[name].evidence == cap.evidence


def test_strict_harness_node_depends_on_pytest(tmp_path: Path) -> None:
    graph = build_capability_graph(tmp_path)
    harness = graph.get(STRICT_HARNESS)
    assert harness is not None
    assert harness.depends_on == ["pytest"]
    # Empty project: no pytest -> strict harness is not ready (graceful, CP-005).
    assert graph.is_ready(STRICT_HARNESS) is False


def test_provider_node_present(tmp_path: Path) -> None:
    graph = build_capability_graph(tmp_path)
    assert any(n.kind == "provider" for n in graph.nodes)


def test_source_only_python_project_detects_python_pytest_and_git(tmp_path: Path) -> None:
    # A real small project: `.py` source + a pytest-style test + a git repo, but
    # NO pyproject.toml/pytest.ini manifest. Manifest-only detection would report
    # nothing; source-evidence detection must surface the genuine capabilities.
    (tmp_path / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_add():\n    assert True\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()

    graph = build_capability_graph(tmp_path)
    by_id = {n.id: n for n in graph.nodes}

    assert by_id["python"].kind == "language"
    assert by_id["pytest"].kind == "test"
    assert by_id["git"].kind == "vcs"
    assert by_id["python"].evidence != ""
    assert by_id["pytest"].evidence != ""
    # All three are genuinely available, and the strict harness becomes ready now
    # that its pytest dependency is satisfied (CP-005).
    ready = graph.available_ids()
    assert {"python", "pytest", "git", STRICT_HARNESS} <= ready


def test_python_node_only_when_python_sources_exist(tmp_path: Path) -> None:
    # Honest: a project with no python sources gets no python/pytest node.
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    by_id = {n.id: n for n in build_capability_graph(tmp_path).nodes}
    assert "python" not in by_id
    assert "pytest" not in by_id


def test_pytest_node_requires_a_test_file_not_just_sources(tmp_path: Path) -> None:
    # A `.py` source with no test file yields python but not pytest (no fabrication).
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    by_id = {n.id: n for n in build_capability_graph(tmp_path).nodes}
    assert by_id["python"].kind == "language"
    assert "pytest" not in by_id


def test_manifest_pytest_evidence_wins_over_source_evidence(tmp_path: Path) -> None:
    # When both a manifest and a test file are present, the manifest-derived
    # pytest node (and its evidence) stays authoritative — no duplicate node.
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")

    nodes = [n for n in build_capability_graph(tmp_path).nodes if n.id == "pytest"]
    assert len(nodes) == 1
    assert nodes[0].evidence == "pyproject.toml or pytest.ini"


def test_vendored_dirs_are_ignored_in_source_scan(tmp_path: Path) -> None:
    # Tests inside vendored/cache dirs must not be treated as project evidence.
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "test_vendored.py").write_text("def test_v():\n    assert True\n", encoding="utf-8")

    by_id = {n.id: n for n in build_capability_graph(tmp_path).nodes}
    assert "pytest" not in by_id
    assert "python" not in by_id
