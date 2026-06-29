"""PersonaResolver — maps a workflow node *role* to a persona (PR-006, book §6).

A workflow node declares a role (``builder``, ``diagnostician``); the resolver maps
it to a persona id, allowing profile and plugin overrides of the default mapping. The
default map is derived from the built-in persona ids (``builder`` -> ``oc-builder``)
and the legacy ``PHASE_PERSONAS`` phase map (``apply`` -> ``oc-builder``), so both a
short role and an SDD phase name resolve.
"""

from __future__ import annotations

from opencontext_core.personas.definition import PersonaDefinition
from opencontext_core.personas.registry import PersonaNotFound, PersonaRegistry


def default_role_map() -> dict[str, str]:
    """Build the default role -> persona-id map from the built-ins.

    Includes both the short role (``oc-builder`` -> ``builder``) and every SDD phase
    name from ``PHASE_PERSONAS`` (``apply`` -> ``oc-builder``).
    """
    from opencontext_core.personas import PERSONAS, PHASE_PERSONAS

    role_map: dict[str, str] = {}
    for persona in PERSONAS:
        role = persona.id[3:] if persona.id.startswith("oc-") else persona.id
        role_map[role] = persona.id
    role_map.update(PHASE_PERSONAS)
    return role_map


class PersonaResolver:
    """Resolves a role to a :class:`PersonaDefinition`, honouring profile overrides."""

    def __init__(
        self,
        registry: PersonaRegistry | None = None,
        role_map: dict[str, str] | None = None,
        overrides: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self.registry = registry or PersonaRegistry.with_builtins()
        self.role_map = role_map if role_map is not None else default_role_map()
        # profile name -> {role -> persona id}. Profiles and plugins layer on top.
        self.overrides = overrides or {}

    def resolve_id(self, role: str, profile: str | None = None) -> str:
        """Resolve a role to a persona id; profile override wins over the default."""
        if profile and profile in self.overrides and role in self.overrides[profile]:
            return self.overrides[profile][role]
        if role in self.role_map:
            return self.role_map[role]
        # A role may already be a concrete persona id.
        if self.registry.has(role):
            return role
        raise PersonaNotFound(f"no persona mapped for role {role!r}")

    def resolve(self, role: str, profile: str | None = None) -> PersonaDefinition:
        """Resolve a role to its persona definition."""
        return self.registry.get(self.resolve_id(role, profile))

    def add_override(self, profile: str, role: str, persona_id: str) -> None:
        """Register a profile/plugin override of the default role mapping."""
        self.overrides.setdefault(profile, {})[role] = persona_id
