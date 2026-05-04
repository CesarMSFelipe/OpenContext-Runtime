"""Memory candidate models used by harvesting and novelty checks."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum
from opencontext_core.models.context import DataClassification


class MemoryKind(StrEnum):
    """Kinds of memory that can be stored in the context repository."""

    FACT = "fact"
    DECISION = "decision"
    CONSTRAINT = "constraint"
    ERROR = "error"
    VALIDATION = "validation"
    SUMMARY = "summary"


class MemoryCandidate(BaseModel):
    """Potential long-term memory extracted from a trace or user-approved source."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(description="Redacted memory candidate content.")
    source: str = Field(description="Trace id, file path, or source reference.")
    kind: MemoryKind = Field(description="Candidate memory kind.")
    novelty_score: float = Field(ge=0.0, le=1.0, description="Estimated novelty.")
    reuse_likelihood: float = Field(ge=0.0, le=1.0, description="Likelihood of future reuse.")
    classification: DataClassification = Field(description="Candidate data classification.")
    token_cost: int = Field(ge=0, description="Estimated token cost.")
    source_trust: float = Field(default=0.5, ge=0.0, le=1.0, description="Source trust score.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Traceable scoring data.")
