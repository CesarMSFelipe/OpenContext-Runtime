"""Code-aware compression policy decisions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum


class CodeCompressionMode(StrEnum):
    """Modes that affect how code may be compacted."""

    PLAN = "plan"
    ARCHITECT = "architect"
    REVIEW = "review"
    IMPLEMENT_PACK = "implement_pack"
    ACT = "act"
    AUDIT = "audit"


class CodeCompressionDecision(BaseModel):
    """Policy decision for code context compression."""

    model_config = ConfigDict(extra="forbid")

    mode: CodeCompressionMode = Field(description="Resolved code context mode.")
    strategy: str = Field(description="Code-aware strategy key.")
    allow_lossy: bool = Field(description="Whether lossy code compression is allowed.")
    preserve_exact_code: bool = Field(description="Whether exact snippets/files must be kept.")
    reason: str = Field(description="Deterministic policy reason.")


class CodeCompressionPolicy:
    """Prevents code from being compressed like prose."""

    def decide(
        self,
        mode: CodeCompressionMode | str,
        *,
        explicitly_allow_lossy: bool = False,
    ) -> CodeCompressionDecision:
        """Return a conservative code-compression decision."""

        resolved = CodeCompressionMode(mode)
        if resolved is CodeCompressionMode.PLAN:
            return CodeCompressionDecision(
                mode=resolved,
                strategy="signatures_summaries_dependencies",
                allow_lossy=explicitly_allow_lossy,
                preserve_exact_code=False,
                reason="plan_mode_prefers_signatures",
            )
        if resolved is CodeCompressionMode.ARCHITECT:
            return CodeCompressionDecision(
                mode=resolved,
                strategy="symbols_relationships_decisions",
                allow_lossy=explicitly_allow_lossy,
                preserve_exact_code=False,
                reason="architect_mode_prefers_relationships",
            )
        if resolved is CodeCompressionMode.REVIEW:
            return CodeCompressionDecision(
                mode=resolved,
                strategy="diff_affected_symbols_related_tests",
                allow_lossy=False,
                preserve_exact_code=True,
                reason="review_mode_preserves_evidence",
            )
        if resolved in {CodeCompressionMode.IMPLEMENT_PACK, CodeCompressionMode.ACT}:
            return CodeCompressionDecision(
                mode=resolved,
                strategy="exact_snippets_files_tests",
                allow_lossy=explicitly_allow_lossy,
                preserve_exact_code=not explicitly_allow_lossy,
                reason="implementation_mode_requires_exact_code",
            )
        return CodeCompressionDecision(
            mode=resolved,
            strategy="security_relevant_code_config_tests",
            allow_lossy=False,
            preserve_exact_code=True,
            reason="audit_mode_preserves_security_evidence",
        )
