"""Project memory facade."""

from __future__ import annotations

from opencontext_core.memory.stores import ProjectMemoryStore
from opencontext_core.models.project import ProjectManifest


class ProjectMemory:
    """Small facade over a project memory store."""

    def __init__(self, store: ProjectMemoryStore) -> None:
        self.store = store

    def save(self, manifest: ProjectManifest) -> None:
        """Save the current project manifest."""

        self.store.save_manifest(manifest)

    def load(self) -> ProjectManifest:
        """Load the current project manifest."""

        return self.store.load_manifest()
