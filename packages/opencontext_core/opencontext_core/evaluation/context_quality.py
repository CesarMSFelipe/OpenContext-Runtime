"""Context quality evaluation for context packs and traces."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.context import ContextPackResult
from opencontext_core.models.trace import RuntimeTrace


class ContextQualityReport(BaseModel):
    """Deterministic context quality report."""

    model_config = ConfigDict(extra="forbid")

    source_count: int = Field(ge=0, description="Included source count.")
    final_input_tokens: int = Field(ge=0, description="Final context or prompt tokens.")
    omitted_tokens: int = Field(ge=0, description="Tokens omitted by packing.")
    coverage_score: float = Field(ge=0.0, le=1.0, description="Source coverage score.")
    noise_score: float = Field(ge=0.0, le=1.0, description="Estimated noise score.")
    quality_risk: str = Field(description="low, medium, or high.")
    warnings: list[str] = Field(default_factory=list, description="Quality warnings.")


class ContextQualityEvaluator:
    """Evaluates whether selected context is likely useful and not too noisy."""

    def evaluate_pack(self, pack: ContextPackResult) -> ContextQualityReport:
        """Evaluate a context pack."""

        omitted_tokens = sum(item.tokens for item in pack.omitted)
        return _report(
            source_count=len(pack.included),
            final_input_tokens=pack.used_tokens,
            omitted_tokens=omitted_tokens,
            available_tokens=pack.available_tokens,
        )

    def evaluate_trace(self, trace: RuntimeTrace) -> ContextQualityReport:
        """Evaluate a runtime trace."""

        final_tokens = trace.token_estimates.get(
            "final_context_pack",
            trace.token_estimates.get("prompt", 0),
        )
        omitted_tokens = sum(item.tokens for item in trace.discarded_context_items)
        return _report(
            source_count=len(trace.selected_context_items),
            final_input_tokens=final_tokens,
            omitted_tokens=omitted_tokens,
            available_tokens=trace.token_budget.available_context_tokens,
        )


def _report(
    *,
    source_count: int,
    final_input_tokens: int,
    omitted_tokens: int,
    available_tokens: int,
) -> ContextQualityReport:
    warnings: list[str] = []
    if source_count == 0:
        warnings.append("missing_sources")
    if available_tokens > 0 and final_input_tokens > available_tokens:
        warnings.append("over_budget")
    total_considered = final_input_tokens + omitted_tokens
    coverage_score = final_input_tokens / total_considered if total_considered > 0 else 0.0
    noise_score = min(1.0, final_input_tokens / max(available_tokens, 1))
    if source_count == 0 or "over_budget" in warnings:
        risk = "high"
    elif coverage_score < 0.2 or noise_score > 0.9:
        risk = "medium"
    else:
        risk = "low"
    return ContextQualityReport(
        source_count=source_count,
        final_input_tokens=final_input_tokens,
        omitted_tokens=omitted_tokens,
        coverage_score=coverage_score,
        noise_score=noise_score,
        quality_risk=risk,
        warnings=warnings,
    )
