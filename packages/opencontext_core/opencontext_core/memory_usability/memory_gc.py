"""Memory garbage collection and pruning."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.memory_usability.context_repository import ContextRepository


class MemoryGCReport(BaseModel):
    """Memory garbage collection report."""

    model_config = ConfigDict(extra="forbid")

    pruned_ids: list[str] = Field(description="Memory ids moved to archive.")
    reason: str = Field(description="GC policy reason.")


class MemoryGarbageCollector:
    """Prunes expired and superseded memory into archive."""

    def __init__(self, repository: ContextRepository) -> None:
        self.repository = repository

    def run(self) -> MemoryGCReport:
        """Run safe local garbage collection."""

        pruned = self.repository.prune_expired()
        return MemoryGCReport(pruned_ids=pruned, reason="expired_or_superseded")
