"""GateResult and HarnessResult — the book's harness output contracts (PR-006).

The legacy ``PhaseGate``/``HarnessRunResult`` (``harness/models.py``) stay the
runtime's working types; these are the book-shaped contracts (doc 07 §8/§9) the
HarnessRegistry produces and PR-007 consumes. ``PhaseGate.to_gate_result()`` and
``HarnessRunResult`` → :func:`harness_result_from_run` adapt the legacy types onto
these without a second source of truth.

Layer L6: imports L0 (compat) + the L6 harness models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.harness.models import GateSeverity, GateStatus, HarnessRunResult


class GateResult(BaseModel):
    """A single gate finding (book doc 07 §9)."""

    model_config = ConfigDict(extra="forbid")

    gate_id: str
    status: GateStatus = GateStatus.PASSED
    severity: GateSeverity = GateSeverity.WARNING
    message: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    blocking: bool = False


class HarnessResult(BaseModel):
    """Structured result of a harness execution (book doc 07 §8)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "opencontext.harness_result.v1"
    harness_id: str
    mode: str = "warn"
    status: GateStatus = GateStatus.PASSED
    summary: str = ""
    gates: list[GateResult] = Field(default_factory=list)
    receipts: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    next_recommended: str | None = None
    # REG-CONV false-positive metric — a noisy harness is measurable/tunable.
    false_positive_rate: float = 0.0

    @property
    def blocking_failures(self) -> list[GateResult]:
        """Gate results that failed and are marked blocking."""
        return [g for g in self.gates if g.status == GateStatus.FAILED and g.blocking]


def harness_result_from_run(
    run: HarnessRunResult, *, harness_id: str, mode: str = "warn"
) -> HarnessResult:
    """Adapt a legacy :class:`HarnessRunResult` onto the book :class:`HarnessResult`."""
    return HarnessResult(
        harness_id=harness_id,
        mode=mode,
        status=run.status,
        summary=run.task,
        gates=[g.to_gate_result() for g in run.gates],
        artifacts=[a.path for a in run.artifacts],
        metrics={"warnings": len(run.warnings)},
        false_positive_rate=run.false_positive_rate,
    )
