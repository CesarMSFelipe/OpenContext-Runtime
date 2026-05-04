"""Technology profile interfaces that keep core framework-agnostic."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.project import FileKind, ProjectFile, Symbol

GENERIC_PROFILE = "generic"


class ProfileDetectionResult(BaseModel):
    """Detection result emitted by a technology profile."""

    model_config = ConfigDict(extra="forbid")

    profile: str = Field(description="Stable technology profile identifier.")
    score: float = Field(ge=0.0, le=1.0, description="Detection confidence.")
    markers: list[str] = Field(
        default_factory=list,
        description="Project-relative markers that contributed to detection.",
    )


class FileClassificationResult(BaseModel):
    """Profile-specific file classification hint."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="Project-relative path.")
    kind: FileKind = Field(description="Suggested high-level file kind.")
    tags: list[str] = Field(default_factory=list, description="Profile-specific tags.")


class ContextProviderReference(BaseModel):
    """Reference to a context provider contributed by a profile."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Provider key.")
    description: str = Field(description="Provider purpose.")


class WorkflowPackReference(BaseModel):
    """Reference to a workflow pack suggested by a profile."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Workflow pack name.")
    mode: str = Field(description="Recommended context mode.")


class SafeCommand(BaseModel):
    """Profile-suggested command that still requires runtime policy approval."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Command identifier.")
    command: tuple[str, ...] = Field(description="Executable and arguments.")
    read_only: bool = Field(default=True, description="Whether the command is expected read-only.")
    network: bool = Field(default=False, description="Whether the command needs network access.")


class TechnologyProfile(Protocol):
    """Optional stack-specific intelligence plugged into the universal core."""

    name: str

    def detect(
        self,
        project_root: Path,
        paths: Sequence[str] = (),
    ) -> ProfileDetectionResult:
        """Detect this technology profile for a project."""

    def classify_file(self, path: Path) -> FileClassificationResult | None:
        """Return a profile-specific classification hint for one path."""

    def extract_symbols(self, file: ProjectFile) -> list[Symbol]:
        """Return extra profile-specific symbols beyond the core extractor."""

    def build_context_providers(self) -> list[ContextProviderReference]:
        """Return context providers exposed by this profile."""

    def suggest_workflows(self) -> list[WorkflowPackReference]:
        """Return workflow packs suggested by this profile."""

    def suggest_validation_commands(self) -> list[SafeCommand]:
        """Return validation command suggestions, never direct execution."""


class GenericTechnologyProfile:
    """Fallback profile for projects without specialized first-party profiles."""

    name = GENERIC_PROFILE

    def detect(
        self,
        project_root: Path,
        paths: Sequence[str] = (),
    ) -> ProfileDetectionResult:
        """Return a generic detection result."""

        markers = ["no technology-specific profile required"] if paths else []
        return ProfileDetectionResult(profile=self.name, score=1.0, markers=markers)

    def classify_file(self, path: Path) -> FileClassificationResult | None:
        """Generic profile does not override core file classification."""

        return None

    def extract_symbols(self, file: ProjectFile) -> list[Symbol]:
        """Generic profile does not add symbols beyond core extraction."""

        return []

    def build_context_providers(self) -> list[ContextProviderReference]:
        """Generic profile does not add specialized context providers."""

        return []

    def suggest_workflows(self) -> list[WorkflowPackReference]:
        """Return universal workflow suggestions."""

        return [
            WorkflowPackReference(name="code-review", mode="review"),
            WorkflowPackReference(name="security-audit", mode="audit"),
        ]

    def suggest_validation_commands(self) -> list[SafeCommand]:
        """Generic profile does not suggest executable validation commands."""

        return []
