"""Reusable secure workflow pack models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class WorkflowPack(BaseModel):
    """Secure reusable context workflow definition."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Pack name.")
    description: str = Field(description="Pack purpose.")
    workflow: str = Field(description="Referenced workflow name.")
    required_policies: list[str] = Field(
        default_factory=list,
        description="Security policy checks required before use.",
    )
