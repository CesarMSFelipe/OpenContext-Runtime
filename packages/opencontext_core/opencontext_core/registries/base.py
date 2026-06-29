"""Shared registry contract pattern (PR-006).

One base pattern reused by the persona, skill, and harness registries so all three
are maintainable governance contracts rather than ad-hoc lookups. A registry is a
keyed, validated collection of *definitions*; a definition is any model carrying a
stable ``id`` plus plugin-ready provenance metadata.

Layering (doc 58): this module lives in L6 (Registries). It imports only L0
contracts (``compat``) and pydantic — never Runtime, harness, agents, workflows, or
brain — so the registry substrate cannot create an upward/circular dependency.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum

# The registry exposes a ``list()`` method (spec) which shadows the builtin ``list``
# inside the class scope where return annotations resolve. This alias captures the
# builtin so the annotations stay correct (mirrors workflows/registry.py).
_List = list


class RegistrySource(StrEnum):
    """Where a registry entry came from (plugin-ready provenance, REG-CONV)."""

    BUILTIN = "builtin"
    USER = "user"
    PROJECT = "project"
    PLUGIN = "plugin"


class TrustLevel(StrEnum):
    """Trust attached to an entry's source. Built-ins are trusted; plugin/community
    entries are untrusted until explicitly promoted (book §27 plugin governance)."""

    TRUSTED = "trusted"
    COMMUNITY = "community"
    UNTRUSTED = "untrusted"


class RegistryMetadata(BaseModel):
    """Plugin-ready provenance carried by every registry entry (REG-CONV).

    The Policy Engine and the cross-reference validator read this to decide whether
    an entry may be loaded and what permissions it declared.
    """

    model_config = ConfigDict(extra="forbid")

    source: RegistrySource = Field(
        default=RegistrySource.BUILTIN, description="Origin of the entry."
    )
    trust: TrustLevel = Field(
        default=TrustLevel.TRUSTED, description="Trust level of the entry's source."
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Capabilities/permissions the entry declares it needs.",
    )
    plugin_id: str | None = Field(
        default=None, description="Owning plugin id when source == plugin."
    )


@runtime_checkable
class Definition(Protocol):
    """Structural contract for anything a :class:`Registry` can hold.

    A definition exposes a stable ``id`` (the registry key) and ``metadata``
    (provenance). ``PersonaDefinition``/``SkillDefinition``/``HarnessDefinition``
    all satisfy this protocol.
    """

    id: str
    metadata: RegistryMetadata


class RegistryError(Exception):
    """Base error for registry operations."""


class RegistryNotFound(KeyError, RegistryError):
    """Raised when an id is not registered (never a silent ``None``)."""


class DuplicateDefinition(RegistryError):
    """Raised when registering an id that already exists without ``replace``."""


class Registry[DefT: Definition]:
    """Generic, validated, keyed collection of definitions.

    Subclasses (``PersonaRegistry`` / ``SkillRegistryV2`` / ``HarnessRegistry``)
    set ``kind`` for error messages and seed built-ins via ``with_builtins``. The
    method surface (``register``/``get``/``has``/``list``/``list_ids``) is identical
    across all three so callers learn one API (Persona/Skill/Harness Internal API,
    doc 59).
    """

    kind: str = "definition"

    def __init__(self) -> None:
        self._defs: dict[str, DefT] = {}

    def register(self, definition: DefT, *, replace: bool = False) -> None:
        """Store ``definition`` keyed by its id; reject silent overwrites."""
        key = definition.id
        if not key:
            raise RegistryError(f"{self.kind} has an empty id")
        if key in self._defs and not replace:
            raise DuplicateDefinition(f"{self.kind} {key!r} already registered")
        self._defs[key] = definition

    def get(self, definition_id: str) -> DefT:
        """Return the definition for ``definition_id``; raise if unknown."""
        try:
            return self._defs[definition_id]
        except KeyError as exc:
            raise RegistryNotFound(f"unknown {self.kind}: {definition_id!r}") from exc

    def has(self, definition_id: str) -> bool:
        """Return True when ``definition_id`` is registered."""
        return definition_id in self._defs

    def list(self) -> _List[DefT]:
        """Return all registered definitions (insertion order)."""
        return list(self._defs.values())

    def list_ids(self) -> _List[str]:
        """Return all registered ids (insertion order)."""
        return list(self._defs.keys())

    def __len__(self) -> int:
        return len(self._defs)
