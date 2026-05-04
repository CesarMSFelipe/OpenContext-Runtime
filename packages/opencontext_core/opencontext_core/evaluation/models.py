"""Evaluation layer models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvalCase(BaseModel):
    """A structural evaluation case for a workflow."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Eval case identifier.")
    workflow: str = Field(description="Workflow to run or inspect.")
    input: str = Field(description="Eval input.")
    expected_sources: list[str] = Field(default_factory=list)
    forbidden_sources: list[str] = Field(default_factory=list)
    expected_behavior: str | None = Field(default=None)
    forbidden_behavior: str | None = Field(default=None)


class EvalResult(BaseModel):
    """Result of evaluating one case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="Eval case identifier.")
    passed: bool = Field(description="Whether the eval passed.")
    score: float = Field(ge=0.0, le=1.0, description="Normalized score.")
    reasons: list[str] = Field(description="Human-readable reasons.")


class ContextBenchCase(BaseModel):
    """Golden case for deterministic context retrieval and token-efficiency checks."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Stable benchmark case identifier.")
    query: str = Field(description="Developer task used to prepare a context pack.")
    expected_sources: list[str] = Field(
        default_factory=list,
        description="Source path fragments that should be present in the packed context.",
    )
    forbidden_sources: list[str] = Field(
        default_factory=list,
        description="Source path fragments that must not be present in the packed context.",
    )
    min_source_coverage: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Minimum expected-source coverage required for this case.",
    )


class ContextBenchCaseResult(BaseModel):
    """Result for one context benchmark case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="Benchmark case identifier.")
    passed: bool = Field(description="Whether this case passed all gates.")
    source_coverage: float = Field(ge=0.0, le=1.0, description="Expected-source hit ratio.")
    token_reduction: float = Field(
        ge=0.0,
        le=1.0,
        description="Token reduction compared with the full indexed project baseline.",
    )
    context_tokens: int = Field(ge=0, description="Prepared context token estimate.")
    baseline_tokens: int = Field(ge=0, description="Full indexed project token estimate.")
    included_sources: list[str] = Field(description="Sources included by the context pack.")
    missing_sources: list[str] = Field(description="Expected source fragments not found.")
    forbidden_hits: list[str] = Field(description="Forbidden source fragments found.")
    reasons: list[str] = Field(description="Human-readable result details.")


class ContextBenchSuiteResult(BaseModel):
    """Aggregate result for a context benchmark suite."""

    model_config = ConfigDict(extra="forbid")

    passed: bool = Field(description="Whether all cases passed.")
    cases: list[ContextBenchCaseResult] = Field(description="Per-case benchmark results.")
    average_source_coverage: float = Field(
        ge=0.0,
        le=1.0,
        description="Average expected-source coverage.",
    )
    average_token_reduction: float = Field(
        ge=0.0,
        le=1.0,
        description="Average token reduction compared with full project context.",
    )
