"""Project indexing and manifest models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum


class FileKind(StrEnum):
    """High-level classification for indexed files."""

    CODE = "code"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    TEST = "test"
    TEMPLATE = "template"
    ASSET = "asset"
    UNKNOWN = "unknown"


class ProjectFile(BaseModel):
    """Indexed file metadata persisted in a project manifest."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Stable file identifier derived from the relative path.")
    path: str = Field(description="Project-relative POSIX path.")
    language: str = Field(description="Detected language or file format.")
    file_type: FileKind = Field(description="High-level file classification.")
    tokens: int = Field(ge=0, description="Estimated token count for the file.")
    size_bytes: int = Field(ge=0, description="File size in bytes.")
    summary: str = Field(description="Short deterministic file summary.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional indexing details such as modification time and profile markers.",
    )


class Symbol(BaseModel):
    """A lightweight symbol extracted from source code."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Stable symbol identifier.")
    name: str = Field(description="Symbol name.")
    kind: str = Field(description="Symbol kind such as class, function, or method.")
    path: str = Field(description="Project-relative path containing the symbol.")
    line: int = Field(ge=1, description="One-based source line number.")
    language: str = Field(description="Language from which the symbol was extracted.")
    container: str | None = Field(
        default=None,
        description="Optional parent symbol, class, namespace, or module.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional extraction metadata.",
    )


class RepoMapEntry(BaseModel):
    """Compact symbol-level overview for one repository file."""

    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(description="Project-relative file path.")
    symbols: list[Symbol] = Field(description="Symbols included for this file.")
    token_estimate: int = Field(ge=0, description="Estimated tokens for the rendered entry.")
    relevance_score: float = Field(default=0.0, ge=0.0, description="Query relevance score.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Traceable repo-map ranking metadata.",
    )


class RepoMap(BaseModel):
    """Compact repository map rendered before loading full file context."""

    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(description="Project name.")
    entries: list[RepoMapEntry] = Field(description="Repo-map entries in ranking order.")
    token_estimate: int = Field(ge=0, description="Estimated tokens for all entries.")
    generated_at: datetime = Field(description="UTC generation timestamp.")


class DependencyEdge(BaseModel):
    """Static dependency relationship between project files or external modules."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(description="Project-relative source path.")
    target: str = Field(description="Resolved project path or external module name.")
    kind: str = Field(description="Dependency kind such as import, require, include, or use.")
    internal: bool = Field(description="Whether target resolved to an indexed project file.")
    line: int = Field(ge=1, description="One-based line number.")


class DependencyGraph(BaseModel):
    """Static dependency graph produced during indexing."""

    model_config = ConfigDict(extra="forbid")

    nodes: list[str] = Field(description="Indexed project file paths.")
    edges: list[DependencyEdge] = Field(description="Dependency edges.")
    unresolved: list[DependencyEdge] = Field(description="External or unresolved edges.")
    generated_at: datetime = Field(description="UTC generation timestamp.")


class ProjectManifest(BaseModel):
    """Persisted project intelligence snapshot used by retrieval and workflows."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    project_name: str = Field(description="Configured project name.")
    root: str = Field(description="Absolute project root path at indexing time.")
    profile: str = Field(description="Configured or detected primary technology profile.")
    technology_profiles: list[str] = Field(
        validation_alias=AliasChoices("technology_profiles", "frameworks"),
        description="Detected technology profiles.",
    )
    files: list[ProjectFile] = Field(description="Indexed project files.")
    symbols: list[Symbol] = Field(description="Extracted project symbols.")
    dependency_graph: DependencyGraph | None = Field(
        default=None,
        description="Static dependency graph, when dependency graph extraction is enabled.",
    )
    generated_at: datetime = Field(description="UTC timestamp when the manifest was generated.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Traceable indexing decisions and summary counts.",
    )

    @property
    def frameworks(self) -> list[str]:
        """Backward-compatible alias for manifests created before profiles were renamed."""

        return self.technology_profiles
