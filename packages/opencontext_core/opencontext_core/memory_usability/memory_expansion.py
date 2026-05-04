"""Memory expansion helpers."""

from __future__ import annotations

from opencontext_core.memory_usability.context_repository import ContextRepository, MemoryItem


class MemoryExpansionTool:
    """Expands compact memory back to its stored redacted body."""

    def __init__(self, repository: ContextRepository) -> None:
        self.repository = repository

    def expand(self, memory_id: str) -> MemoryItem:
        """Return a stored item for user-approved expansion."""

        item = self.repository.get(memory_id)
        if not item.source:
            raise ValueError("memory expansion requires a source reference")
        return item
