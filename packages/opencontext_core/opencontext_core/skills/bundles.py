"""Persona skill bundles (PR-006, book doc 06 — Skill Bundles).

A bundle is the per-persona set of skills the runtime resolves when that persona
drives a node. Bundles are data, not prompts: the resolver loads them and the
cross-reference validator asserts every id resolves in the Skill registry.
"""

from __future__ import annotations

# persona id -> ordered skill ids. Mirrors each persona's required + optional skills
# (book §Skill Bundles). Every id must resolve in the SkillRegistryV2 built-ins.
PERSONA_BUNDLES: dict[str, list[str]] = {
    "oc-orchestrator": ["oc-plan-lite"],
    "oc-explorer": [
        "oc-context-discovery",
        "oc-symbol-retrieval",
        "oc-test-discovery",
        "oc-owner-discovery",
    ],
    "oc-context-engineer": ["oc-context-discovery", "oc-memory-grounding"],
    "oc-requirements": ["oc-acceptance-criteria", "oc-risk-evaluation"],
    "oc-architect": ["oc-task-decomposition", "oc-plan-lite"],
    "oc-planner": ["oc-task-decomposition", "oc-acceptance-criteria"],
    "oc-builder": [
        "oc-apply-surgical",
        "oc-local-first-validation",
        "oc-refactor-safe",
    ],
    "oc-tester": ["oc-test-selection", "oc-local-first-validation"],
    "oc-harness-verifier": ["oc-local-first-validation", "oc-lint-analysis"],
    "oc-reviewer": ["oc-review-changes", "oc-maintainability-review"],
    "oc-diagnostician": [
        "oc-three-hypotheses",
        "oc-root-cause-analysis",
        "oc-semantic-gc",
    ],
    "oc-security-reviewer": ["oc-security-review"],
    "oc-archivist": [
        "oc-memory-candidate",
        "oc-kg-update",
        "oc-summary",
        "oc-receipt-finalization",
    ],
    "oc-evolution-steward": ["oc-risk-evaluation"],
    "oc-professor": ["oc-context-discovery"],
}


def bundle_for(persona_id: str) -> list[str]:
    """Return the skill ids bundled for ``persona_id`` (empty list if none)."""
    return list(PERSONA_BUNDLES.get(persona_id, []))
