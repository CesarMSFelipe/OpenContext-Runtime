"""Canonical policy decision contracts (PR-005 — Policy Contract v1).

One canonical :class:`PolicyDecision` (``allow``/``warn``/``ask``/``deny`` plus
``reason``, ``policy_id``, ``evidence_refs`` and ``required_approval``) is the
single shape every governed operation resolves to (SPEC PE-2). A
:class:`PolicyReceipt` records the human/auto resolution of an ``ask`` decision
(SPEC APPROVAL-2).

``models/run_envelope.py`` keeps a *serialized* ``PolicyDecision`` (a lower L0
evidence record) so the envelope never imports this L3 governance type; the
:meth:`PolicyDecision.to_envelope` adapter converts a canonical decision into
that record for attachment to ``RunEnvelope.policy_decisions`` (CONV.5).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import UTC
from opencontext_core.runtime.ids import new_decision_id, new_receipt_id

if TYPE_CHECKING:
    from opencontext_core.models.run_envelope import PolicyDecision as EnvelopePolicyDecision

# Internal contract version (doc 59 §Internal contract versioning). A guard test
# asserts this value so an accidental breaking change is caught.
POLICY_CONTRACT_VERSION = 1

# Event family for policy-layer events (doc 59 §Event hierarchy). Studio renders
# one lane per family.
POLICY_EVENT_FAMILY = "policy"

# The four canonical decisions (SPEC PE-2 / PE-3).
DecisionVerb = Literal["allow", "warn", "ask", "deny"]

# Execution posture stamped on each decision (CONV.4 remote/CI fail-closed).
PolicyMode = Literal["interactive", "ci"]


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


class PolicyDecision(BaseModel):
    """The canonical, runtime-enforced decision for one governed operation.

    Produced by :class:`~opencontext_core.policy.engine.PolicyEngine`. ``deny``
    decisions MUST carry a non-empty :attr:`remediation` (CONV.5 actionable
    denial). ``mode`` records whether the decision was finalised interactively or
    under fail-closed CI/remote execution (CONV.4).
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "opencontext.policy_decision.v1"
    contract_version: int = POLICY_CONTRACT_VERSION
    decision_id: str = Field(default_factory=new_decision_id)
    operation: str
    decision: DecisionVerb
    reason: str
    policy_id: str
    evidence_refs: list[str] = Field(default_factory=list)
    required_approval: bool = False
    # Actionable next-action for a ``deny`` (allowed alternative or required
    # approval). Empty for non-deny decisions (CONV.5).
    remediation: str = ""
    mode: PolicyMode = "interactive"
    created_at: str = Field(default_factory=_now_iso)

    @property
    def allowed(self) -> bool:
        """True only when the operation may proceed now (``allow`` or ``warn``)."""
        return self.decision in ("allow", "warn")

    def to_envelope(self) -> EnvelopePolicyDecision:
        """Project this decision onto the L0 ``RunEnvelope`` evidence record."""
        # Imported here (not at module load) so the L0 envelope never depends on
        # this L3 module — the dependency points downward only.
        from opencontext_core.models.run_envelope import PolicyDecision as EnvelopeDecision

        return EnvelopeDecision(
            id=self.decision_id,
            subject=self.operation,
            operation=self.operation,
            decision=self.decision,
            reason=self.reason,
            policy=self.policy_id,
            policy_id=self.policy_id,
            evidence_refs=list(self.evidence_refs),
            required_approval=self.required_approval,
            remediation=self.remediation,
            metadata={"mode": self.mode},
        )


class PolicyReceipt(BaseModel):
    """Evidence receipt recording how an ``ask`` decision was resolved (APPROVAL-2)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "opencontext.policy_receipt.v1"
    receipt_id: str = Field(default_factory=new_receipt_id)
    decision_id: str
    operation: str
    outcome: Literal["approved", "denied", "auto_applied"]
    evidence_refs: list[str] = Field(default_factory=list)
    approved_by: str | None = None
    created_at: str = Field(default_factory=_now_iso)
