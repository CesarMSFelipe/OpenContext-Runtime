from __future__ import annotations

import json
from pathlib import Path

from conftest import write_config

from opencontext_cli.main import (
    _agent_context,
    _check,
    _checkpoint,
    _ddev,
    _debug,
    _doctor,
    _drupal,
    _eval,
    _evidence,
    _governance,
    _init,
    _orchestrate,
    _pack,
    _pack_diff,
    _packs,
    _propose,
    _provider_simulate,
    _run,
    _security,
    _tokens,
    _validate,
    _watch,
)
from opencontext_core.config import SecurityMode
from opencontext_core.runtime import OpenContextRuntime


def test_check_scaffold_creates_files(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    _check("run", "all")
    output = capsys.readouterr().out
    paths = json.loads(output)
    assert any(path.endswith("security-review.md") for path in paths)


def test_checkpoint_create_outputs_hashes(capsys) -> None:
    _checkpoint("create")
    output = capsys.readouterr().out
    data = json.loads(output)
    assert "project_hash" in data
    assert data["trace_id"] == "scaffold-trace"


def test_security_scan_outputs_warning(capsys) -> None:
    _security("scan")
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data["warnings"]


def test_pack_diff_scaffold(capsys) -> None:
    _pack_diff("main", "HEAD")
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "scaffold"


def test_eval_scaffold_commands(capsys) -> None:
    runtime = OpenContextRuntime()
    _eval(runtime, "security", None, ".", 6000, 0.5)
    security = json.loads(capsys.readouterr().out)
    assert security["suite"] == "security"


def test_tokens_and_watch_scaffolds(capsys) -> None:
    _tokens("report")
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ready"
    _watch(".")
    assert "scaffold" in capsys.readouterr().out


def test_agent_context_copy_fallback(capsys) -> None:
    _agent_context("review auth", "plan", 1000, copy=True)
    out = capsys.readouterr().out
    assert "Agent Context" in out


def test_doctor_tokens_suggest_ignore(tmp_path: Path, capsys) -> None:
    from opencontext_core.runtime import OpenContextRuntime

    runtime = OpenContextRuntime(storage_path=tmp_path / ".storage/opencontext")
    _doctor(runtime, "tokens", suggest_ignore=True)
    data = json.loads(capsys.readouterr().out)
    assert "suggested_opencontextignore" in data


def test_init_template_creates_workspace_and_config(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    _init("opencontext.yaml", "enterprise")
    out = capsys.readouterr().out
    assert "Template: enterprise" in out
    assert (tmp_path / "opencontext.yaml").exists()
    assert (tmp_path / ".opencontext/policies/security-policy.yaml").exists()


def test_ddev_init_scaffolds_wrapper(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    _ddev("init")
    out = capsys.readouterr().out
    assert "DDEV" in out
    assert (tmp_path / ".ddev/commands/web/opencontext").exists()
    assert (tmp_path / ".opencontext/workflows/drupal-review.yaml").exists()


def test_agentic_scaffold_commands_report_safe_policies(capsys) -> None:
    _orchestrate("requirements.md", SecurityMode.PRIVATE_PROJECT)
    orchestrate = json.loads(capsys.readouterr().out)
    assert orchestrate["policy"]["safe_commands"]["decision"] == "ask"
    assert orchestrate["policy"]["write_file"]["decision"] == "deny"

    _debug("var/log/error.log", "safe", SecurityMode.PRIVATE_PROJECT)
    debug = json.loads(capsys.readouterr().out)
    assert debug["network"]["allowed"] is False

    _validate("drupal", SecurityMode.PRIVATE_PROJECT)
    validate = json.loads(capsys.readouterr().out)
    assert validate["run_tests"]["decision"] == "ask"

    _propose("patch", "Fix sk-abcdefghijklmnopqrstuvwxyz123456", SecurityMode.PRIVATE_PROJECT)
    propose = json.loads(capsys.readouterr().out)
    assert propose["file_writes_performed"] is False
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in propose["task"]


def test_more_required_scaffolds(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "workflow-packs/example").mkdir(parents=True)
    (tmp_path / "workflow-packs/example/workflow.yaml").write_text("name: example\n")

    _packs("list")
    assert json.loads(capsys.readouterr().out) == ["example"]
    _packs("inspect", "example")
    assert json.loads(capsys.readouterr().out)["status"] == "available"
    _drupal("tests", "plan")
    assert json.loads(capsys.readouterr().out)["profile"] == "drupal"
    _run("architect", "Design access boundaries", None)
    assert json.loads(capsys.readouterr().out)["mode"] == "architect"


def test_provider_governance_and_evidence_scaffolds(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config_path = write_config(tmp_path, project)
    runtime = OpenContextRuntime(config_path=config_path, storage_path=tmp_path / ".storage")

    _provider_simulate("openai", "confidential", runtime)
    provider = json.loads(capsys.readouterr().out)
    assert provider["decision"]["allowed"] is False

    _governance("report", runtime)
    governance = json.loads(capsys.readouterr().out)
    assert governance["external_providers_enabled"] is False

    _evidence("pack", runtime)
    evidence = json.loads(capsys.readouterr().out)
    assert evidence["raw_secrets_included"] is False


def test_pack_output_file_is_redacted(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    (project / "auth.py").write_text(f"API_KEY = '{secret}'\n", encoding="utf-8")
    config_path = write_config(tmp_path, project)
    runtime = OpenContextRuntime(config_path=config_path, storage_path=tmp_path / ".storage")
    runtime.index_project(project)
    output = tmp_path / ".opencontext/context-packs/auth.md"

    _pack(runtime, "API_KEY", 2000, "markdown", "audit", False, str(output))

    assert "Wrote context pack" in capsys.readouterr().out
    rendered = output.read_text(encoding="utf-8")
    assert secret not in rendered
    assert "Security Warnings" in rendered
