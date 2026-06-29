"""Named policy events (SPEC EVENT-1).

Every policy evaluation emits ``policy.evaluated`` plus one verb-specific event;
denials/violations additionally emit their category-specific event
(``command.blocked``, ``network.blocked``, ``secret.detected``). Events are
published through the PR-001 :class:`~opencontext_core.runtime.event_bus.EventBus`
and belong to the ``policy`` family (doc 59 §Event hierarchy); the
non-``policy.``-prefixed names carry ``metadata["family"]="policy"`` so Studio
still groups them on the policy lane.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from opencontext_core.policy.models import POLICY_EVENT_FAMILY
from opencontext_core.runtime.events import make_event

if TYPE_CHECKING:
    from opencontext_core.policy.models import PolicyDecision
    from opencontext_core.runtime.event_bus import EventBus
    from opencontext_core.runtime.events import RuntimeEvent

# Canonical policy event names (architecture §EVENT-1).
POLICY_EVALUATED = "policy.evaluated"
POLICY_ALLOWED = "policy.allowed"
POLICY_WARNED = "policy.warned"
POLICY_ASK = "policy.ask"
POLICY_DENIED = "policy.denied"
POLICY_APPROVED = "policy.approved"
POLICY_VIOLATION = "policy.violation"
SECRET_DETECTED = "secret.detected"
NETWORK_BLOCKED = "network.blocked"
COMMAND_BLOCKED = "command.blocked"

_VERB_EVENT = {
    "allow": POLICY_ALLOWED,
    "warn": POLICY_WARNED,
    "ask": POLICY_ASK,
    "deny": POLICY_DENIED,
}


def event_types_for(decision: PolicyDecision) -> list[str]:
    """Return the ordered event names a decision emits (``policy.evaluated`` first)."""
    types = [POLICY_EVALUATED, _VERB_EVENT[decision.decision]]
    # ``secret.detected`` fires whenever a secret was involved, whether the sink
    # was blocked (deny) or sanitized (warn) — evidence carries ``secret:<kind>``
    # or the reason names a raw secret.
    if any(ref.startswith("secret:") for ref in decision.evidence_refs) or (
        "secret" in decision.reason
    ):
        types.append(SECRET_DETECTED)
    if decision.decision == "deny":
        # Category-specific blocked/violation events for denials.
        op = decision.operation
        if op == "command":
            types.append(COMMAND_BLOCKED)
        elif op == "network":
            types.append(NETWORK_BLOCKED)
        types.append(POLICY_VIOLATION)
    return types


def emit_policy_events(
    bus: EventBus | None,
    *,
    session_id: str,
    decision: PolicyDecision,
    run_id: str | None = None,
) -> list[RuntimeEvent]:
    """Publish the policy events for *decision* and return them.

    No-op (returns ``[]``) when no bus or session id is supplied — the engine
    still produces and records the decision; events are an additive sink.
    """
    if bus is None or not session_id:
        return []
    events: list[RuntimeEvent] = []
    for event_type in event_types_for(decision):
        event = make_event(
            session_id=session_id,
            run_id=run_id,
            type=event_type,
            status=decision.decision,
            message=decision.reason,
            metadata={
                "family": POLICY_EVENT_FAMILY,
                "policy_id": decision.policy_id,
                "operation": decision.operation,
                "decision_id": decision.decision_id,
                "mode": decision.mode,
            },
        )
        events.append(bus.publish(event))
    return events
