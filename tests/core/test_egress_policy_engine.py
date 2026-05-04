from __future__ import annotations

from opencontext_core.operating_model import EgressPolicyEngine


def test_egress_policy_engine_denies_network_by_default() -> None:
    decision = EgressPolicyEngine().evaluate("network")

    assert decision.allowed is False
    assert decision.decision == "deny"
