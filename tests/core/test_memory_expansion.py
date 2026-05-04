from __future__ import annotations

from pathlib import Path

from opencontext_core.memory_usability import ContextRepository, MemoryExpansionTool


def test_memory_expansion_requires_source_ref(tmp_path: Path) -> None:
    repo = ContextRepository(tmp_path)
    item = repo.store("Expandable redacted memory.", kind="summary", source="trace:abc")

    expanded = MemoryExpansionTool(repo).expand(item.id)

    assert expanded.content == "Expandable redacted memory."
