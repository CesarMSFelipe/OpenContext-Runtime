"""Safety policy skeletons for v0.1."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OutputSchemaValidator(BaseModel):
    """Placeholder result model for future structured output validation."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False, description="Schema validation is disabled in v0.1.")
