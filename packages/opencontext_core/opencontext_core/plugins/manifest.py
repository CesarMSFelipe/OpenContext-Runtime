"""Plugin manifest models with explicit, deny-by-default permissions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.context import DataClassification


class PluginPermissions(BaseModel):
    """Explicit plugin permissions. All capabilities default to denied."""

    model_config = ConfigDict(extra="forbid")

    read_paths: list[str] = Field(default_factory=list, description="Allowlisted read paths.")
    write_paths: list[str] = Field(default_factory=list, description="Allowlisted write paths.")
    network_hosts: list[str] = Field(
        default_factory=list,
        description="Allowlisted outbound hosts. Empty means no network access.",
    )
    mcp_servers: list[str] = Field(default_factory=list, description="Allowlisted MCP servers.")


class PluginManifest(BaseModel):
    """Manifest for loading secure OpenContext plugins."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Stable plugin identifier.")
    version: str = Field(description="Plugin semantic version.")
    type: str = Field(default="analyzer", description="Plugin category.")
    description: str = Field(default="", description="Human-readable plugin description.")
    entrypoint: str = Field(description="Python entrypoint path for plugin activation.")
    max_data_classification: DataClassification = Field(
        default=DataClassification.INTERNAL,
        description="Maximum classification the plugin is allowed to process.",
    )
    permissions: PluginPermissions = Field(
        default_factory=PluginPermissions,
        description="Explicit permission grant set.",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional plugin metadata."
    )
