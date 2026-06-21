"""Tests for the loop CLI command."""


def test_loop_dry_run_exits_zero():
    import argparse

    from opencontext_cli.commands.loop_cmd import handle_loop

    args = argparse.Namespace(
        task="fix bug",
        flow="quick",
        compress="efficient",
        root=".",
        max_rounds=1,
        autonomous=False,
        dry_run=True,
    )
    assert handle_loop(args) == 0


def test_loop_flows_defined():
    from opencontext_cli.commands.loop_cmd import FLOWS

    assert "quick" in FLOWS
    assert "autonomous" in FLOWS
    assert "full" in FLOWS


def test_apply_outcome_reports_planned_vs_written(tmp_path):
    """C4: the loop must be honest about whether apply wrote real source."""
    import json
    from types import SimpleNamespace

    from opencontext_cli.commands.loop_cmd import _apply_outcome

    planned = tmp_path / "apply-manifest.json"
    planned.write_text(json.dumps({"status": "planned", "changes": []}), encoding="utf-8")
    note = _apply_outcome([SimpleNamespace(path=str(planned))])
    assert note is not None and "planned-only" in note

    written = tmp_path / "written" / "apply-manifest.json"
    written.parent.mkdir()
    written.write_text(
        json.dumps({"status": "applied", "changes": [{"path": "a.py"}]}), encoding="utf-8"
    )
    note2 = _apply_outcome([SimpleNamespace(path=str(written))])
    assert note2 is not None and "wrote 1 file" in note2
