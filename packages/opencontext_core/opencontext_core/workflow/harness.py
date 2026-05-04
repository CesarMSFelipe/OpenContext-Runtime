"""Controlled agent harness planning without native tool execution."""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.tools.policy import (
    ToolCallDecision,
    ToolExecutionMode,
    ToolPermission,
    ToolPermissionPolicy,
    evaluate_tool_call,
)


class HarnessPolicy(BaseModel):
    """Deterministic guardrails for one controlled harness run."""

    model_config = ConfigDict(extra="forbid")

    max_turns: int = Field(default=50, ge=1, description="Maximum model/tool turns.")
    auto_compact_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Input token ratio that triggers compaction before the next turn.",
    )
    allow_parallel_tools: bool = Field(
        default=False,
        description="Whether independent allowed tool calls may execute in parallel.",
    )
    tool_policy: ToolPermissionPolicy = Field(
        default_factory=ToolPermissionPolicy,
        description="Tool permission policy used by the harness.",
    )


class ToolCallRequest(BaseModel):
    """Planned tool call capability request."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(description="Requested tool name.")
    requires_write: bool = Field(default=False, description="Whether the call writes state.")
    requires_network: bool = Field(default=False, description="Whether the call needs network.")
    permission: ToolPermission | None = Field(
        default=None,
        description="Explicit tool permission, when configured.",
    )


class ToolCallPlan(BaseModel):
    """Harness decision for one requested tool call."""

    model_config = ConfigDict(extra="forbid")

    request: ToolCallRequest = Field(description="Original tool call request.")
    decision: ToolCallDecision = Field(description="Permission decision.")


class HarnessTurnState(BaseModel):
    """Current harness run state used for continuation and compaction decisions."""

    model_config = ConfigDict(extra="forbid")

    turn_index: int = Field(default=0, ge=0, description="Zero-based turn index.")
    input_tokens: int = Field(default=0, ge=0, description="Current prompt/input token count.")
    max_input_tokens: int = Field(gt=0, description="Maximum model input token budget.")
    pending_tool_calls: list[ToolCallRequest] = Field(
        default_factory=list,
        description="Tool calls proposed for the next tool execution phase.",
    )


class HarnessPreflight(BaseModel):
    """Preflight plan for a controlled harness turn."""

    model_config = ConfigDict(extra="forbid")

    phases: list[str] = Field(description="Ordered harness phases for this turn.")
    compact_required: bool = Field(description="Whether context compaction should run first.")
    continue_run: bool = Field(description="Whether the harness may continue.")
    tool_plans: list[ToolCallPlan] = Field(description="Per-tool permission decisions.")
    execution_mode: ToolExecutionMode = Field(description="Effective tool execution mode.")
    reasons: list[str] = Field(description="Traceable planning reasons.")


class ControlledHarnessPlanner:
    """Plans harness turns with compaction, permission, and continuation checks."""

    phases: ClassVar[list[str]] = [
        "preprocessing",
        "llm_streaming",
        "error_recovery",
        "tool_execution",
        "continuation_check",
    ]

    def plan_turn(
        self,
        state: HarnessTurnState,
        policy: HarnessPolicy | None = None,
    ) -> HarnessPreflight:
        """Return a deterministic preflight plan for one harness turn."""

        effective_policy = policy or HarnessPolicy()
        reasons: list[str] = []
        token_ratio = state.input_tokens / state.max_input_tokens
        compact_required = token_ratio >= effective_policy.auto_compact_threshold
        if compact_required:
            reasons.append("auto_compact_threshold_reached")
        continue_run = state.turn_index < effective_policy.max_turns
        if not continue_run:
            reasons.append("max_turns_reached")
        tool_plans = [
            ToolCallPlan(
                request=request,
                decision=self._decide_tool(request, effective_policy.tool_policy),
            )
            for request in state.pending_tool_calls
        ]
        if tool_plans and not effective_policy.allow_parallel_tools:
            reasons.append("serial_tool_execution")
        return HarnessPreflight(
            phases=list(self.phases),
            compact_required=compact_required,
            continue_run=continue_run,
            tool_plans=tool_plans,
            execution_mode=effective_policy.tool_policy.mode,
            reasons=reasons,
        )

    def _decide_tool(
        self,
        request: ToolCallRequest,
        policy: ToolPermissionPolicy,
    ) -> ToolCallDecision:
        if request.tool_name in policy.denied_tools:
            return ToolCallDecision(
                allowed=False,
                reason="tool_denied_by_harness_policy",
                pipeline=["deny_rule"],
            )
        if not policy.allows(request.tool_name):
            return ToolCallDecision(
                allowed=False,
                reason="tool_not_allowlisted",
                pipeline=["deny_rule", "tool_check_permission"],
            )
        return evaluate_tool_call(
            request.permission,
            security_mode=policy.security_mode,
            mode=policy.mode,
            always_allowed=request.tool_name in policy.always_allowed_tools,
            requires_write=request.requires_write,
            requires_network=request.requires_network,
        )
