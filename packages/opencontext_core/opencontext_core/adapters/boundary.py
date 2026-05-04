"""Adapter boundary models for external coding surfaces."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum


class AdapterTarget(StrEnum):
    """Supported integration targets at the boundary layer."""

    CODEX = "codex"
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    WINDSURF = "windsurf"
    OPENCODE = "opencode"
    OPENCLAW = "openclaw"


class AdapterRequest(BaseModel):
    """Inbound request from an adapter to OpenContext."""

    model_config = ConfigDict(extra="forbid")

    target: AdapterTarget = Field(description="Caller adapter target.")
    task: str = Field(description="Task or question for context operations.")
    workflow_pack: str | None = Field(default=None, description="Optional workflow pack name.")
