from __future__ import annotations

from opencontext_core.tools import ToolExecutionMode, ToolPermissionPolicy
from opencontext_core.workflow import (
    ControlledHarnessPlanner,
    HarnessPolicy,
    HarnessTurnState,
    ToolCallRequest,
)


def test_harness_preflight_triggers_compaction_and_serial_tool_reason() -> None:
    policy = HarnessPolicy(
        auto_compact_threshold=0.75,
        tool_policy=ToolPermissionPolicy(
            always_allowed_tools={"inspect"},
            mode=ToolExecutionMode.READ_ONLY,
        ),
    )
    state = HarnessTurnState(
        turn_index=1,
        input_tokens=800,
        max_input_tokens=1000,
        pending_tool_calls=[ToolCallRequest(tool_name="inspect")],
    )

    plan = ControlledHarnessPlanner().plan_turn(state, policy)

    assert plan.compact_required is True
    assert plan.continue_run is True
    assert plan.tool_plans[0].decision.allowed is True
    assert plan.reasons == ["auto_compact_threshold_reached", "serial_tool_execution"]


def test_harness_preflight_denies_write_in_read_only_mode() -> None:
    policy = HarnessPolicy(
        tool_policy=ToolPermissionPolicy(
            always_allowed_tools={"edit"},
            mode=ToolExecutionMode.READ_ONLY,
        ),
    )
    state = HarnessTurnState(
        turn_index=0,
        input_tokens=10,
        max_input_tokens=1000,
        pending_tool_calls=[ToolCallRequest(tool_name="edit", requires_write=True)],
    )

    plan = ControlledHarnessPlanner().plan_turn(state, policy)

    assert plan.tool_plans[0].decision.allowed is False
    assert plan.tool_plans[0].decision.reason == "read_only_blocks_write"
