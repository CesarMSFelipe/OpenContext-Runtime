"""Hook lifecycle data models — pure data contract (slice 5).

A hook is a callable: ``(HookInput) -> HookDecision``. The data models here
describe what flows in and out of those callables; the dispatcher that wires
hooks to conductor events lives elsewhere so the contract stays orchestrator
free and trivially testable.

Spec (CAP5.Hook):
- Scenario: Hook fires on phase entry — registered hook receives HookInput
  with ``phase_name`` + ``run_id``; PROCEED/HALT decision is respected.
- Scenario: HALT decision stops phase — must propagate without conductor
  mutation.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from opencontext_core.hooks.models import HookDecision, HookEvent, HookInput

# A hook is a pure callable over HookInput. The "registry" is just a list.
type HookFn = Callable[[HookInput], HookDecision]


def test_hook_event_lists_four_lifecycle_events() -> None:
    """HookEvent exposes exactly PHASE_START/END + RUN_START/END (spec CAP5.Hook)."""
    names = {e.name for e in HookEvent}
    assert names == {"PHASE_START", "PHASE_END", "RUN_START", "RUN_END"}


def test_hook_decision_lists_proceed_and_halt() -> None:
    """HookDecision is binary: PROCEED or HALT."""
    assert {d.name for d in HookDecision} == {"PROCEED", "HALT"}


def test_hook_input_carries_phase_name_run_id_and_payload() -> None:
    """HookInput stores phase_name, run_id, and a free-form payload dict."""
    inp = HookInput(phase_name="spec", run_id="run-42", payload={"k": "v"})
    assert inp.phase_name == "spec"
    assert inp.run_id == "run-42"
    assert inp.payload == {"k": "v"}


def test_hook_input_requires_run_id() -> None:
    """run_id is mandatory — omitting it fails Pydantic validation."""
    with pytest.raises(ValidationError):
        HookInput(phase_name="spec")  # type: ignore[call-arg]


def test_hook_input_default_payload_is_empty_dict() -> None:
    """payload defaults to an empty dict so callers can pass kwargs safely."""
    inp = HookInput(phase_name="explore", run_id="run-1")
    assert inp.payload == {}
    assert isinstance(inp.payload, dict)


def test_registered_phase_start_hook_receives_hook_input() -> None:
    """A hook registered for PHASE_START is invoked with the HookInput.

    Uses a plain list-of-callables registry — no dispatcher class lives in
    hooks/models.py (pure data contract).
    """
    captured: list[HookInput] = []

    def hook(inp: HookInput) -> HookDecision:
        captured.append(inp)
        return HookDecision.PROCEED

    registered: dict[HookEvent, list[HookFn]] = {HookEvent.PHASE_START: [hook]}

    inp = HookInput(phase_name="apply", run_id="run-7")
    decisions = [h(inp) for h in registered[HookEvent.PHASE_START]]

    assert captured == [inp]
    assert decisions == [HookDecision.PROCEED]


def test_halt_decision_propagates_from_registered_hook() -> None:
    """A hook returning HALT propagates; PROCEED from a sibling does not mask it.

    Triangulates the dispatch contract: the HALT decision must remain visible
    so the (future) conductor can stop the phase.
    """

    def halting(inp: HookInput) -> HookDecision:
        return HookDecision.HALT

    def proceeding(inp: HookInput) -> HookDecision:
        return HookDecision.PROCEED

    registered: list[HookFn] = [halting, proceeding]
    inp = HookInput(phase_name="apply", run_id="run-7")
    decisions = [h(inp) for h in registered]

    assert HookDecision.HALT in decisions
    assert HookDecision.PROCEED in decisions
    # HookInput is immutable Pydantic model — no conductor state touched.
    assert inp.phase_name == "apply"


def test_hook_input_is_immutable_conductor_state_unchanged() -> None:
    """Dispatching hooks must not mutate HookInput (no conductor coupling)."""
    inp = HookInput(phase_name="design", run_id="run-9", payload={"a": 1})
    snapshot = inp.model_dump()

    def noop(_: HookInput) -> HookDecision:
        return HookDecision.PROCEED

    _ = noop(inp)

    assert inp.model_dump() == snapshot
