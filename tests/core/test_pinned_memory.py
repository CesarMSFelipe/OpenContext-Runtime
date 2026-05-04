from __future__ import annotations

from pathlib import Path

from opencontext_core.memory_usability import ContextRepository, PinnedMemoryManager


def test_pinned_memory_manager_updates_pin(tmp_path: Path) -> None:
    repo = ContextRepository(tmp_path)
    item = repo.store("Critical invariant.", kind="fact", source="trace:abc")

    pinned = PinnedMemoryManager(repo).pin(item.id)

    assert pinned.pin is True
