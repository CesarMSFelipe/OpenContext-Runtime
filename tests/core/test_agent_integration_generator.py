from __future__ import annotations

from pathlib import Path

from opencontext_core.adapters.agent_manifest import AgentIntegrationGenerator, AgentTarget


def test_agent_integration_generator_creates_cursor_rule(tmp_path: Path) -> None:
    generated = AgentIntegrationGenerator().generate(tmp_path, target=AgentTarget.CURSOR)

    rule_path = tmp_path / ".cursor" / "rules" / "opencontext.mdc"
    assert generated[0].created is True
    assert rule_path.exists()
    assert "opencontext pack" in rule_path.read_text(encoding="utf-8")


def test_agent_integration_generator_creates_windsurf_rule(tmp_path: Path) -> None:
    AgentIntegrationGenerator().generate(tmp_path, target=AgentTarget.WINDSURF)

    rule_path = tmp_path / ".windsurf" / "rules" / "opencontext.md"
    assert rule_path.exists()
    assert "Windsurf" in rule_path.read_text(encoding="utf-8")


def test_agent_integration_generator_creates_opencode_files(tmp_path: Path) -> None:
    AgentIntegrationGenerator().generate(tmp_path, target=AgentTarget.OPENCODE)

    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "opencode.json").exists()
    assert "AGENTS.md" in (tmp_path / "opencode.json").read_text(encoding="utf-8")


def test_agent_integration_generator_does_not_overwrite_without_force(tmp_path: Path) -> None:
    agents_path = tmp_path / "AGENTS.md"
    agents_path.write_text("custom", encoding="utf-8")

    generated = AgentIntegrationGenerator().generate(tmp_path, target=AgentTarget.CODEX)

    assert generated[0].created is False
    assert agents_path.read_text(encoding="utf-8") == "custom"
