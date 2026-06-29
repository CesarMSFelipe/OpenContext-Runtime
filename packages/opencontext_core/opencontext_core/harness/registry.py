"""HarnessRegistry — registry-driven harness resolution (PR-006, book doc 07 §6).

Seeds the 13 built-in :class:`HarnessDefinition`s from ``builtins/*.yaml``, each
binding the gate ids already implemented in ``gates.py``/``config.py``. Registering
a new harness requires no Runtime change — only ``register()`` (book §30). When
``runtime.harness_registry_enabled`` is off, the legacy phase→gate path in
``HarnessConfig``/``HarnessRunner`` runs unchanged.
"""

from __future__ import annotations

from opencontext_core.harness.builtins import builtins_dir
from opencontext_core.harness.definition import HarnessDefinition
from opencontext_core.registries.base import Registry, RegistryNotFound
from opencontext_core.registries.loader import load_defs_from_dir

__all__ = ["HarnessNotFound", "HarnessRegistry"]


class HarnessNotFound(RegistryNotFound):
    """Raised when a harness id is not registered."""


class HarnessRegistry(Registry[HarnessDefinition]):
    """Registers, retrieves, and lists harness definitions."""

    kind = "harness"

    def get(self, definition_id: str) -> HarnessDefinition:
        try:
            return super().get(definition_id)
        except RegistryNotFound as exc:
            raise HarnessNotFound(str(exc)) from exc

    @classmethod
    def with_builtins(cls) -> HarnessRegistry:
        """Construct a registry seeded with every built-in harness definition."""
        registry = cls()
        for defn in load_defs_from_dir(builtins_dir(), HarnessDefinition):
            registry.register(defn)
        return registry
