"""Progressive disclosure memory selection."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import UTC
from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.memory_usability.context_repository import ContextRepository, MemoryItem
from opencontext_core.models.context import DataClassification


class MemoryInjectionPlan(BaseModel):
    """Memory selected for prompt injection and items kept expandable."""

    model_config = ConfigDict(extra="forbid")

    included: list[MemoryItem] = Field(description="Pinned and relevant compact memory.")
    omitted: list[MemoryItem] = Field(description="Memory not injected.")
    expandable: list[str] = Field(description="Memory ids whose originals can be expanded.")
    used_tokens: int = Field(ge=0, description="Injected memory token estimate.")
    omitted_tokens: int = Field(ge=0, description="Omitted memory token estimate.")


class ProgressiveDisclosureMemory:
    """Selects pinned memory and relevant facts without dumping the repository."""

    def __init__(self, repository: ContextRepository) -> None:
        self.repository = repository

    def select(
        self,
        query: str,
        *,
        max_tokens: int = 2000,
        allowed_classifications: set[DataClassification] | None = None,
    ) -> MemoryInjectionPlan:
        """Build a progressive memory injection plan."""

        allowed = allowed_classifications or {
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
            DataClassification.CONFIDENTIAL,
        }
        all_items = [item for item in self.repository.list_items() if _injectable(item, allowed)]
        candidates = [
            _with_search_metadata(result.item, result.score, result.reason)
            for result in self.repository.search_results(query)
            if _injectable(result.item, allowed)
        ]
        pinned = [item for item in all_items if item.pin]
        ordered: list[MemoryItem] = []
        seen: set[str] = set()
        for item in [*pinned, *candidates]:
            if item.id not in seen:
                ordered.append(item)
                seen.add(item.id)
        included: list[MemoryItem] = []
        omitted: list[MemoryItem] = []
        used_tokens = 0
        for item in ordered:
            if used_tokens + item.tokens <= max_tokens:
                included.append(item)
                used_tokens += item.tokens
            else:
                omitted.append(item)
        omitted.extend(item for item in all_items if item.id not in seen)
        return MemoryInjectionPlan(
            included=included,
            omitted=omitted,
            expandable=[item.id for item in included if item.source],
            used_tokens=used_tokens,
            omitted_tokens=sum(estimate_tokens(item.content) for item in omitted),
        )


def _injectable(item: MemoryItem, allowed: set[DataClassification]) -> bool:
    now = datetime.now(tz=UTC)
    if item.valid_until is not None and item.valid_until <= now:
        return False
    return item.classification in allowed and item.superseded_by is None


def _with_search_metadata(item: MemoryItem, score: float, reason: str) -> MemoryItem:
    metadata = dict(item.metadata)
    metadata["memory_search"] = {"score": score, "reason": reason}
    return item.model_copy(update={"metadata": metadata})
