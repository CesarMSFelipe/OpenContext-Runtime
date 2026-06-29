"""Risk-based auto-apply policy (SPEC AUTO-1).

Maps a proposed change's risk to a canonical decision: low → ``allow``,
medium → ``ask``, high → ``deny``. High risk is triggered by auth, billing,
secrets, migrations, deletes, or network/export changes; medium by multi-file or
public-API changes, or any change lacking tests; otherwise low.
"""

from __future__ import annotations

from opencontext_core.compat import StrEnum
from opencontext_core.policy.models import PolicyDecision

_POLICY_ID = "policy.auto_apply"

# Path substrings that mark a change as high-risk (deny auto-apply).
_HIGH_RISK_MARKERS = (
    "auth",
    "login",
    "oauth",
    "session",
    "password",
    "credential",
    "billing",
    "payment",
    "invoice",
    "charge",
    "secret",
    "token",
    "apikey",
    "api_key",
    ".env",
    "migration",
    "migrations",
    "schema.sql",
    "alembic",
    "egress",
    "firewall",
    "network",
)


class ChangeRisk(StrEnum):
    """Risk tier of a proposed change."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AutoApplyPolicy:
    """Adjudicate whether a proposed change may be auto-applied (SPEC AUTO-1)."""

    def classify(
        self,
        *,
        changed_paths: list[str] | None = None,
        has_deletes: bool = False,
        touches_network_or_export: bool = False,
        touches_public_api: bool = False,
        has_tests: bool = True,
    ) -> ChangeRisk:
        """Classify the risk tier from change signals."""
        paths = [p.lower() for p in (changed_paths or [])]
        if has_deletes or touches_network_or_export:
            return ChangeRisk.HIGH
        if any(marker in path for path in paths for marker in _HIGH_RISK_MARKERS):
            return ChangeRisk.HIGH
        if touches_public_api or not has_tests or len(paths) > 1:
            return ChangeRisk.MEDIUM
        return ChangeRisk.LOW

    def evaluate(
        self,
        *,
        changed_paths: list[str] | None = None,
        has_deletes: bool = False,
        touches_network_or_export: bool = False,
        touches_public_api: bool = False,
        has_tests: bool = True,
    ) -> PolicyDecision:
        """Return a canonical decision for auto-applying the change."""
        risk = self.classify(
            changed_paths=changed_paths,
            has_deletes=has_deletes,
            touches_network_or_export=touches_network_or_export,
            touches_public_api=touches_public_api,
            has_tests=has_tests,
        )
        return self.evaluate_risk(risk, changed_paths=changed_paths)

    def evaluate_risk(
        self, risk: ChangeRisk, *, changed_paths: list[str] | None = None
    ) -> PolicyDecision:
        """Map a known risk tier to a canonical decision."""
        evidence = [f"path:{p}" for p in (changed_paths or [])]
        if risk is ChangeRisk.LOW:
            return PolicyDecision(
                operation="auto_apply",
                decision="allow",
                reason="low_risk_change",
                policy_id=_POLICY_ID,
                evidence_refs=evidence,
            )
        if risk is ChangeRisk.MEDIUM:
            return PolicyDecision(
                operation="auto_apply",
                decision="ask",
                reason="medium_risk_requires_approval",
                policy_id=_POLICY_ID,
                evidence_refs=evidence,
                required_approval=True,
            )
        return PolicyDecision(
            operation="auto_apply",
            decision="deny",
            reason="high_risk_change_denied",
            policy_id=_POLICY_ID,
            evidence_refs=evidence,
            remediation="Apply manually after human review; split high-risk paths out.",
        )
