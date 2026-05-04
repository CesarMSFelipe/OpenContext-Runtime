"""Instruction importer for common ecosystem rule files."""

from __future__ import annotations

from pathlib import Path

SOURCES: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    ".clinerules",
    ".roorules",
    ".github/copilot-instructions.md",
)


class ImportedInstruction:
    def __init__(self, source: str, content: str, trusted: bool = False) -> None:
        self.source = source
        self.content = content
        self.trusted = trusted


def import_instructions(root: Path) -> list[ImportedInstruction]:
    imported: list[ImportedInstruction] = []
    for source in SOURCES:
        path = root / source
        if path.exists() and path.is_file():
            imported.append(
                ImportedInstruction(source=source, content=path.read_text(encoding="utf-8"))
            )
    return imported
