"""Cross-reference validation across the persona/skill/harness registries (REG-CONV).

Registries are deterministic governance components: every reference a persona makes
to a skill or harness, and every harness a skill requires, MUST resolve to a
registered id. A dangling reference fails validation rather than surfacing as a
runtime ``KeyError`` mid-flow.

Layer L6: imports only L0 contracts and the local base. Reads referenced ids off
the definitions duck-typed (``required_skills`` / ``required_harnesses`` /
``capabilities.required_*``) so it never imports the concrete definition modules,
keeping the validator free of upward dependencies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DanglingReference(BaseModel):
    """One unresolved cross-reference."""

    model_config = ConfigDict(extra="forbid")

    owner_kind: str = Field(description="Kind of the referencing entry, e.g. 'persona'.")
    owner_id: str = Field(description="Id of the referencing entry.")
    ref_kind: str = Field(description="Kind of the missing target, e.g. 'skill'.")
    ref_id: str = Field(description="The id that did not resolve.")


class CrossRefReport(BaseModel):
    """Result of validating cross-references between registries."""

    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(description="True when no dangling references were found.")
    checked: int = Field(default=0, description="Number of references checked.")
    dangling: list[DanglingReference] = Field(default_factory=list)


class CrossReferenceError(ValueError):
    """Raised when a persona/skill references an unregistered skill/harness."""


def _required_skill_ids(persona: Any) -> list[str]:
    """Collect skill ids a persona requires (flat field + capabilities seam)."""
    ids: list[str] = list(getattr(persona, "required_skills", []) or [])
    caps = getattr(persona, "capabilities", None)
    if caps is not None:
        ids += list(getattr(caps, "required_skills", []) or [])
        ids += list(getattr(caps, "optional_skills", []) or [])
    ids += list(getattr(persona, "optional_skills", []) or [])
    return list(dict.fromkeys(ids))


def _required_harness_ids(owner: Any) -> list[str]:
    """Collect harness ids an owner (persona or skill) requires."""
    ids: list[str] = list(getattr(owner, "required_harnesses", []) or [])
    caps = getattr(owner, "capabilities", None)
    if caps is not None:
        ids += list(getattr(caps, "required_harnesses", []) or [])
    return list(dict.fromkeys(ids))


def validate_cross_references(
    personas: list[Any],
    skills: list[Any],
    harnesses: list[Any],
) -> CrossRefReport:
    """Validate that every persona→skill, persona→harness, and skill→harness
    reference resolves to a registered id (REG-CONV plugin-ready cross-refs).

    Returns a report; callers wanting a hard failure call :func:`ensure_cross_references`.
    """
    skill_ids = {s.id for s in skills}
    harness_ids = {h.id for h in harnesses}

    dangling: list[DanglingReference] = []
    checked = 0

    for persona in personas:
        for skill_id in _required_skill_ids(persona):
            checked += 1
            if skill_id not in skill_ids:
                dangling.append(
                    DanglingReference(
                        owner_kind="persona",
                        owner_id=persona.id,
                        ref_kind="skill",
                        ref_id=skill_id,
                    )
                )
        for harness_id in _required_harness_ids(persona):
            checked += 1
            if harness_id not in harness_ids:
                dangling.append(
                    DanglingReference(
                        owner_kind="persona",
                        owner_id=persona.id,
                        ref_kind="harness",
                        ref_id=harness_id,
                    )
                )

    for skill in skills:
        for harness_id in _required_harness_ids(skill):
            checked += 1
            if harness_id not in harness_ids:
                dangling.append(
                    DanglingReference(
                        owner_kind="skill",
                        owner_id=skill.id,
                        ref_kind="harness",
                        ref_id=harness_id,
                    )
                )

    return CrossRefReport(ok=not dangling, checked=checked, dangling=dangling)


def ensure_cross_references(
    personas: list[Any],
    skills: list[Any],
    harnesses: list[Any],
) -> CrossRefReport:
    """Like :func:`validate_cross_references` but raises on a dangling reference."""
    report = validate_cross_references(personas, skills, harnesses)
    if not report.ok:
        first = report.dangling[0]
        raise CrossReferenceError(
            f"{first.owner_kind} {first.owner_id!r} references unknown "
            f"{first.ref_kind} {first.ref_id!r} "
            f"({len(report.dangling)} dangling reference(s) total)"
        )
    return report
