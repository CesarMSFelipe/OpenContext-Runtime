from __future__ import annotations

from pathlib import Path

from opencontext_core.memory_usability import ContextRepository, MemoryGarbageCollector


def test_memory_gc_archives_superseded_items(tmp_path: Path) -> None:
    repo = ContextRepository(tmp_path)
    item = repo.store("Old decision.", kind="decision", source="trace:abc")
    path, stored = repo._find_path(item.id)
    repo._write_item(stored.model_copy(update={"superseded_by": "mem-new"}), path.parent.name)

    report = MemoryGarbageCollector(repo).run()

    assert item.id in report.pruned_ids
