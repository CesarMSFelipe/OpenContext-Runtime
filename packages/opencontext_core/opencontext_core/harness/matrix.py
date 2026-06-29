"""Workflow → harness → mode matrix (PR-006, book doc 07 §23/§26).

The SDD matrix maps each harness to its default mode for the SDD workflow. REG-CONV
adds strictness-by-profile: the active execution profile (PR-000.2 — ``balanced`` /
``low-cost`` / ``enterprise`` / ``research`` / ``performance``) can raise or lower a
harness's mode deterministically, so strictness is profile-driven, not hardcoded.

The full OC Flow matrix and plugin-harness loading are DEFERRED to PR-007/PR-015
(spec AC-HA6).

Layer L6: imports only the L6 harness definition/registry (for default_mode fallback).
"""

from __future__ import annotations

from opencontext_core.harness.definition import HarnessMode
from opencontext_core.harness.registry import HarnessRegistry

# Book §23 — SDD default harness modes.
SDD_HARNESS_MATRIX: dict[str, HarnessMode] = {
    "context": "strict",
    "planning": "strict",
    "protocol": "warn",
    "mutation": "strict",
    "inspection": "warn",
    "diagnosis": "warn",
    "review": "strict",
    "security": "warn",
    "escalation": "warn",
    "memory": "strict",
    "kg": "strict",
    "consolidation": "strict",
    "evaluation": "warn",
}

# REG-CONV — execution profile → harness mode overrides. Only the deltas from the
# SDD baseline are listed; everything else inherits the baseline. Enterprise raises
# the safety-critical harnesses to strict; low-cost relaxes the expensive ones.
PROFILE_HARNESS_OVERRIDES: dict[str, dict[str, HarnessMode]] = {
    "enterprise": {
        "security": "strict",
        "inspection": "strict",
        "review": "strict",
        "protocol": "strict",
        "evaluation": "strict",
    },
    "low-cost": {
        "security": "warn",
        "inspection": "warn",
        "review": "warn",
        "evaluation": "off",
    },
    "research": {
        "evaluation": "strict",
        "diagnosis": "strict",
    },
    "performance": {
        "evaluation": "strict",
    },
    "balanced": {},
}


def mode_blocks(mode: str) -> bool:
    """True when a harness mode blocks the run on gate failure (strict only)."""
    return mode == "strict"


# --------------------------------------------------------------------------- OC Flow
# PR-007 — the OC Flow harness matrix (book doc 04 §17, extended). OC Flow is the
# operational workflow; its postures are stricter than SDD's around mutation and
# inspection and add three postures beyond ``off``/``warn``/``strict``:
#   - ``strict-lite``: strict but does NOT block on an advisory-only gate (book §9
#     "planning is intentionally lighter").
#   - ``conditional``: runs only when the harness's capability/risk condition holds
#     (Security runs only on a risk-bearing change).
#   - ``optional``: warn-equivalent; the harness may be skipped (Review).
# Authored additively — the SDD matrix above is untouched.
OCFlowPosture = str  # one of: off|warn|strict|strict-lite|conditional|optional

OC_FLOW_HARNESS_MATRIX: dict[str, OCFlowPosture] = {
    "context": "strict",
    "planning": "strict-lite",
    "protocol": "strict",
    "mutation": "strict",
    "inspection": "strict",
    "diagnosis": "strict",
    "review": "optional",
    "security": "conditional",
    "escalation": "strict",
    "memory": "strict",
    "kg": "strict",
    "consolidation": "strict",
    "evaluation": "warn",
}


def oc_flow_posture_blocks(posture: str, *, condition_met: bool = True) -> bool:
    """True when an OC Flow posture blocks the run on gate failure (book §17).

    ``strict`` blocks; ``strict-lite`` blocks on a non-advisory failure; ``conditional``
    blocks only when its capability/risk ``condition_met``; ``optional``/``warn``/``off``
    never block.
    """
    if posture == "strict":
        return True
    if posture == "strict-lite":
        return True
    if posture == "conditional":
        return condition_met
    return False


def resolve_oc_flow_harness_mode(
    harness_id: str,
    *,
    profile: str | None = None,
    registry: HarnessRegistry | None = None,
) -> OCFlowPosture:
    """Resolve an OC Flow harness posture (FLOW-9).

    Precedence: profile override (reuses :data:`PROFILE_HARNESS_OVERRIDES`) > OC Flow
    matrix > harness definition ``default_mode`` (when ``registry`` given) > ``"warn"``.
    A profile override may only *raise* strictness, never relax a strict posture
    (book §6 — the Brain/profile may strengthen, never weaken a harness).
    """
    base = OC_FLOW_HARNESS_MATRIX.get(harness_id)
    if profile and profile in PROFILE_HARNESS_OVERRIDES:
        override = PROFILE_HARNESS_OVERRIDES[profile].get(harness_id)
        if override is not None and not (base == "strict" and override != "strict"):
            return override
    if base is not None:
        return base
    if registry is not None and registry.has(harness_id):
        return registry.get(harness_id).default_mode
    return "warn"


def resolve_harness_mode(
    harness_id: str,
    profile: str | None = None,
    *,
    registry: HarnessRegistry | None = None,
) -> HarnessMode:
    """Resolve a harness's effective mode (REG-CONV strictness-by-profile).

    Precedence: profile override > SDD matrix baseline > the harness definition's
    ``default_mode`` (when ``registry`` is supplied) > ``"warn"``.
    """
    if profile and profile in PROFILE_HARNESS_OVERRIDES:
        override = PROFILE_HARNESS_OVERRIDES[profile].get(harness_id)
        if override is not None:
            return override
    if harness_id in SDD_HARNESS_MATRIX:
        return SDD_HARNESS_MATRIX[harness_id]
    if registry is not None and registry.has(harness_id):
        return registry.get(harness_id).default_mode
    return "warn"
