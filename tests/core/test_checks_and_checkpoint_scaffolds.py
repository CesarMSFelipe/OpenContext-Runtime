from pathlib import Path

from opencontext_core.dx.checkpoints import ContextCheckpoint, fingerprint
from opencontext_core.dx.checks import ensure_checks
from opencontext_core.dx.security_reports import scan_project


def test_ensure_checks_creates_files(tmp_path: Path) -> None:
    paths = ensure_checks(tmp_path)
    assert len(paths) == 5
    for path in paths:
        assert path.exists()


def test_checkpoint_fingerprint_and_model() -> None:
    value = fingerprint("x")
    assert len(value) == 64
    checkpoint = ContextCheckpoint(
        project_hash=value,
        manifest_hash=value,
        repo_map_hash=value,
        policy_hash=value,
        context_pack_hash=value,
        prompt_hash=value,
        trace_id="trace-1",
    )
    assert checkpoint.trace_id == "trace-1"


def test_security_scan_has_warning_without_findings(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("safe project", encoding="utf-8")
    result = scan_project(tmp_path)
    assert result.findings == []
    assert result.warnings
