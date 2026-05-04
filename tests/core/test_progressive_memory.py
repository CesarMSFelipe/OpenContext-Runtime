from __future__ import annotations

from pathlib import Path

from opencontext_core.memory_usability import ContextRepository, ProgressiveDisclosureMemory
from opencontext_core.models.context import DataClassification


def test_pinned_memory_considered_and_non_relevant_omitted(tmp_path: Path) -> None:
    repo = ContextRepository(tmp_path)
    pinned = repo.store(
        "Access control uses AccessResolver.",
        kind="fact",
        source="trace:1",
        pin=True,
    )
    other = repo.store("Billing webhooks use Stripe.", kind="fact", source="trace:2")

    plan = ProgressiveDisclosureMemory(repo).select("access control")

    assert pinned.id in {item.id for item in plan.included}
    assert other.id in {item.id for item in plan.omitted}


def test_secret_memory_not_injected_by_default(tmp_path: Path) -> None:
    repo = ContextRepository(tmp_path)
    secret = repo.store(
        "Secret deployment key exists.",
        kind="fact",
        source="trace:1",
        classification=DataClassification.SECRET,
        pin=True,
    )

    plan = ProgressiveDisclosureMemory(repo).select("deployment")

    assert secret.id not in {item.id for item in plan.included}
