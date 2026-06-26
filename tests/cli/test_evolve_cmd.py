"""Tests for evolve approve/reject/apply --json flag (REQ-7)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


def _run_evolve(argv: list[str], tmp_path: Path, monkeypatch: object) -> tuple[int, str, str]:
    """Run opencontext CLI with given argv; return (rc, stdout, stderr)."""
    import io

    from opencontext_cli.main import main

    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    with (
        patch.object(sys, "argv", ["opencontext", *argv]),
        patch("sys.stdout", new_callable=io.StringIO) as mock_out,
        patch("sys.stderr", new_callable=io.StringIO) as mock_err,
    ):
        try:
            main()
            rc = 0
        except SystemExit as e:
            rc = int(e.code or 0)
        return rc, mock_out.getvalue(), mock_err.getvalue()


def _make_proposal(tmp_path: Path, proposal_id: str, status: str = "proposed") -> None:
    """Write a minimal EvolutionProposal JSON to the store location."""
    from opencontext_core.learning.evolution import EvolutionProposal
    from opencontext_core.learning.evolution_store import EvolutionStore

    proposal = EvolutionProposal(
        proposal_id=proposal_id,
        kind="context_weight",
        status=status,  # type: ignore[arg-type]
        title="Test proposal",
        rationale="test",
    )
    EvolutionStore(tmp_path).save(proposal)


def test_evolve_approve_json(tmp_path: Path, monkeypatch: object) -> None:
    """evolve approve <id> --json must output valid JSON with id and status keys."""
    _make_proposal(tmp_path, "test-approve-1", "proposed")
    rc, stdout, _stderr = _run_evolve(
        ["evolve", "approve", "test-approve-1", "--json"],
        tmp_path,
        monkeypatch,
    )
    assert rc == 0, f"Expected rc=0, got rc={rc}, stderr={_stderr!r}"
    data = json.loads(stdout)
    assert "id" in data, f"Missing 'id' key in JSON output: {data}"
    assert "status" in data, f"Missing 'status' key in JSON output: {data}"
    assert data["id"] == "test-approve-1"
    assert data["status"] == "approved"


def test_evolve_reject_json(tmp_path: Path, monkeypatch: object) -> None:
    """evolve reject <id> --json must output valid JSON with id and status keys."""
    _make_proposal(tmp_path, "test-reject-1", "proposed")
    rc, stdout, _stderr = _run_evolve(
        ["evolve", "reject", "test-reject-1", "--json"],
        tmp_path,
        monkeypatch,
    )
    assert rc == 0, f"Expected rc=0, got rc={rc}, stderr={_stderr!r}"
    data = json.loads(stdout)
    assert "id" in data, f"Missing 'id' key in JSON output: {data}"
    assert "status" in data, f"Missing 'status' key in JSON output: {data}"
    assert data["id"] == "test-reject-1"
    assert data["status"] == "rejected"


def test_evolve_apply_json(tmp_path: Path, monkeypatch: object) -> None:
    """evolve apply <id> --json must output valid JSON with id and status keys."""
    _make_proposal(tmp_path, "test-apply-1", "approved")
    # Patch EvolutionApplier.apply to return a successful result without real I/O.
    mock_result = MagicMock()
    mock_result.applied = True
    mock_result.changed_files = []
    with patch(
        "opencontext_cli.commands.evolve_cmd.EvolutionApplier"
        if False
        else "opencontext_core.learning.evolution_apply.EvolutionApplier.apply",
        return_value=mock_result,
    ):
        rc, stdout, _stderr = _run_evolve(
            ["evolve", "apply", "test-apply-1", "--json"],
            tmp_path,
            monkeypatch,
        )
    assert rc == 0, f"Expected rc=0, got rc={rc}, stderr={_stderr!r}"
    data = json.loads(stdout)
    assert "id" in data, f"Missing 'id' key in JSON output: {data}"
    assert "status" in data, f"Missing 'status' key in JSON output: {data}"
    assert data["id"] == "test-apply-1"
    assert data["status"] == "applied"
