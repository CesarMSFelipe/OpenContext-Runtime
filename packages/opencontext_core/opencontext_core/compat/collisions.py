"""Name-collision resolution policy (SPEC CL-009).

The Runtime vNext program introduces symbols whose names already exist in the
legacy code. Each known collision is registered here with exactly one resolution
rule and the owning PR, so the rename lands before the colliding vNext symbol is
introduced and no import ripple occurs at apply time.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CollisionRule(StrEnum):
    """How a name collision is resolved."""

    alias = "alias"  # keep both; export an alias from one to the other
    namespace = "namespace"  # disambiguate by package (legacy vs runtime.*)
    supersede = "supersede"  # vNext replaces legacy; legacy shimmed then removed


class NameCollision(BaseModel):
    """One legacy<->vNext name collision and its resolution."""

    model_config = ConfigDict(extra="forbid")

    name: str
    legacy_path: str
    vnext_owner_pr: str
    rule: CollisionRule
    note: str


# The four audited collisions (_INDEX-refined-runtime-vnext.md cross-cutting notes).
COLLISION_REGISTRY: list[NameCollision] = [
    NameCollision(
        name="ProviderGateway",
        legacy_path="llm/provider_gateway.py",
        vnext_owner_pr="PR-012",
        rule=CollisionRule.namespace,
        note="legacy per-provider adapter shim (llm.provider_gateway.ProviderGateway, "
        "KEPT as-is for the runtime.gateway_enabled=False path) vs the PR-012 unified "
        "facade (providers.gateway.ProviderGateway, L7 over Policy). Disambiguated by "
        "package per this namespace rule (the recorded example said runtime.*; the "
        "facade landed in providers.* to match L7 layering and the gateway-module "
        "ownership). The facade composes the shim's adapter-build path "
        "(llm.provider_gateway.build_adapter) rather than forking a second one.",
    ),
    NameCollision(
        name="CostReport",
        legacy_path="operating_model/performance.py",
        vnext_owner_pr="PR-011",
        rule=CollisionRule.namespace,
        note="legacy aggregate-ledger CostReport (operating_model.performance) kept "
        "as-is; the PR-011 book estimate-vs-actual CostReport lives in "
        "models/intelligence.py — disambiguated by package (design DEC-2).",
    ),
    NameCollision(
        name="EvolutionProposal",
        legacy_path="learning/evolution.py",
        vnext_owner_pr="PR-011",
        rule=CollisionRule.alias,
        note="legacy EvolutionProposal aliased to the PR-011 book EvolutionCandidate.",
    ),
    NameCollision(
        name="EvidenceRef",
        legacy_path="models/evidence.py",
        vnext_owner_pr="PR-008",
        rule=CollisionRule.supersede,
        note="minimal legacy EvidenceRef superseded by the PR-008 EvidenceRef v2.",
    ),
]


def collision(name: str) -> NameCollision | None:
    """Look up the resolution rule for a colliding *name*."""
    for entry in COLLISION_REGISTRY:
        if entry.name == name:
            return entry
    return None
