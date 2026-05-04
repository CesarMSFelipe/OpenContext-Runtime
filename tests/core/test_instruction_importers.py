from pathlib import Path

from opencontext_core.dx.instructions import import_instructions


def test_instruction_importer_reads_supported_files(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("claude", encoding="utf-8")
    imported = import_instructions(tmp_path)
    assert {item.source for item in imported} == {"AGENTS.md", "CLAUDE.md"}
