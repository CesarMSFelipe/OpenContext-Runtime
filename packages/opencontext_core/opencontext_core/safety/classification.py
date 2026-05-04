"""Classification validation helpers."""

from __future__ import annotations

from opencontext_core.models.context import AssembledPrompt, ContextItem, DataClassification


def enforce_classification_invariants(
    selected: list[ContextItem], discarded: list[ContextItem], prompt: AssembledPrompt | None
) -> None:
    """Fail closed if context-carrying objects miss valid classifications."""

    for item in [*selected, *discarded]:
        if item.classification not in DataClassification:
            raise ValueError(f"Invalid classification on context item {item.id}")
    if prompt is None:
        return
    for section in prompt.sections:
        if section.classification not in DataClassification:
            raise ValueError(f"Invalid classification on prompt section {section.name}")
