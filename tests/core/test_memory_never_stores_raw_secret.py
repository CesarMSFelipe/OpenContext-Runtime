from __future__ import annotations

from pathlib import Path

from opencontext_core.memory_usability import ContextRepository


def test_memory_never_stores_raw_secret(tmp_path: Path) -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    repo = ContextRepository(tmp_path)
    item = repo.store(f"Key is {secret}", kind="fact", source="trace:abc")
    path = tmp_path / ".opencontext/context-repository/memory" / f"{item.id}.md"

    assert secret not in path.read_text(encoding="utf-8")
