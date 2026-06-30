"""ContextReceipt — unified receipt model composing agentic, substrate, and savings reports.

Re-exports ``AgenticReceipt`` and ``ContextSubstrateReport`` from their authoritative
modules and introduces ``ContextReceipt`` as a composition wrapper.

``ContextReceipt.passed_quality_gate()`` returns ``True`` when
``estimated_savings_ratio >= 0.0`` and ``degraded=False`` on the savings report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.agentic.context_substrate import (
    ContextSubstrateBuilder as ContextSubstrateBuilder,
)
from opencontext_core.agentic.context_substrate import (
    ContextSubstrateReport as ContextSubstrateReport,
)

# Re-exports — preserves existing import surfaces.
from opencontext_core.agentic.receipt import AgenticReceipt as AgenticReceipt
from opencontext_core.context.savings import (
    ContextSavingsReport as ContextSavingsReport,
)
from opencontext_core.models.context import (
    CompressionStrategy,
    ContextOmission,
    RetrievalStrategy,
)

# Budget decision recorded on a BudgetReceipt (book §Garbage Collection / §Budget).
BudgetDecision = Literal["fit", "compressed", "gc", "overflow"]


class QueryReceipt(BaseModel):
    """Receipt #1 (book §Retrieval Receipts): the strategy + sources consulted."""

    model_config = ConfigDict(extra="forbid")

    strategy: RetrievalStrategy = Field(description="Retrieval strategy chosen for the node.")
    sources: list[str] = Field(default_factory=list, description="Sources consulted, ordered.")
    query: str = Field(default="", description="The task/query the plan answered.")
    candidate_count: int = Field(default=0, ge=0, description="Candidates the planner ranked.")


class BudgetReceipt(BaseModel):
    """Receipt #2 (book §Retrieval Receipts): estimate vs. limit + the decision."""

    model_config = ConfigDict(extra="forbid")

    token_estimate: int = Field(ge=0, description="Assembled envelope token estimate.")
    budget: int = Field(ge=0, description="Resolved per-node token budget.")
    decision: BudgetDecision = Field(description="fit | compressed | gc | overflow.")
    mode: str = Field(default="warn", description="Budget enforcement mode (off/warn/strict).")
    status: str = Field(default="passed", description="Enforcer ledger status.")


class CompressionReceipt(BaseModel):
    """Receipt #3 (book §Retrieval Receipts): per-strategy compression savings."""

    model_config = ConfigDict(extra="forbid")

    strategy: CompressionStrategy = Field(
        default=CompressionStrategy.NONE, description="Compression strategy applied."
    )
    tokens_before: int = Field(default=0, ge=0, description="Tokens before compression.")
    tokens_after: int = Field(default=0, ge=0, description="Tokens after compression.")

    @property
    def tokens_saved(self) -> int:
        """Tokens removed by compression (never negative)."""
        return max(0, self.tokens_before - self.tokens_after)


class OmissionReceipt(BaseModel):
    """Receipt #4 (book §Retrieval Receipts): what was dropped and why."""

    model_config = ConfigDict(extra="forbid")

    omissions: list[ContextOmission] = Field(
        default_factory=list, description="Traceable omission records for the build."
    )


class RetrievalReceipts(BaseModel):
    """The four typed receipts a single retrieval emits (out-of-band metadata).

    Receipts are carried beside the envelope, never injected into the prompt body —
    they must not consume the budget they account for (design decision #9).
    """

    model_config = ConfigDict(extra="forbid")

    query: QueryReceipt = Field(description="Strategy + sources consulted.")
    budget: BudgetReceipt = Field(description="Estimate vs. limit + decision.")
    compression: CompressionReceipt = Field(
        default_factory=CompressionReceipt, description="Compression strategy + savings."
    )
    omission: OmissionReceipt = Field(
        default_factory=OmissionReceipt, description="Items dropped + reasons."
    )


@dataclass
class ContextReceipt:
    """Unified receipt composing agentic, substrate, and savings sub-reports."""

    agentic: AgenticReceipt | None = None
    substrate: ContextSubstrateReport | None = None
    savings: ContextSavingsReport | None = None

    def passed_quality_gate(self) -> bool:
        """Return True when the savings report is real (not degraded) and ratio >= 0.0.

        A degraded report (ContextPackBuilder absent) always fails the gate.
        A non-degraded report with ratio = 0.0 passes (zero savings is valid).
        """
        if self.savings is None:
            return False
        if self.savings.degraded:
            return False
        return self.savings.estimated_savings_ratio >= 0.0

    @classmethod
    def build_degraded(cls, reason: str = "") -> ContextReceipt:
        """Build a receipt with a degraded savings report."""
        savings = ContextSavingsReport(
            degraded=True,
            warning=reason or "ContextPackBuilder unavailable; savings not measured.",
            tokens_saved=0,
            tokens_without_pack=0,
            estimated_savings_ratio=0.0,
        )
        return cls(savings=savings)
