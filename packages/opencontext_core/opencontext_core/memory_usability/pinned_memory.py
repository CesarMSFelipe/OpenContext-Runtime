"""Pinned memory management."""

from __future__ import annotations

from opencontext_core.memory_usability.context_repository import ContextRepository, MemoryItem


class PinnedMemoryManager:
    """Thin manager for pinning and unpinning context repository items."""

    def __init__(self, repository: ContextRepository) -> None:
        self.repository = repository

    def pin(self, memory_id: str) -> MemoryItem:
        """Pin one memory item."""

        return self.repository.set_pin(memory_id, True)

    def unpin(self, memory_id: str) -> MemoryItem:
        """Unpin one memory item."""

        return self.repository.set_pin(memory_id, False)
