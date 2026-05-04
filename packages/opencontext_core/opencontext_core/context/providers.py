"""Context provider scaffolds returning classified ContextItem objects."""

from __future__ import annotations

from opencontext_core.models.context import ContextItem, ContextPriority, DataClassification


def provider_repo_map(content: str) -> ContextItem:
    return ContextItem(
        id="provider:repo_map",
        content=content,
        source="@repo_map",
        source_type="provider",
        priority=ContextPriority.P1,
        tokens=len(content.split()),
        score=1.0,
        classification=DataClassification.INTERNAL,
        trusted=True,
    )


def provider_security_report(content: str) -> ContextItem:
    return ContextItem(
        id="provider:security_report",
        content=content,
        source="@security_report",
        source_type="provider",
        priority=ContextPriority.P0,
        tokens=len(content.split()),
        score=1.0,
        classification=DataClassification.INTERNAL,
        trusted=True,
    )
