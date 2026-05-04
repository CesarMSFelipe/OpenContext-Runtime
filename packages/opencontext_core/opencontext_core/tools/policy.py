"""Tool permission policies."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum
from opencontext_core.config import SecurityMode


class ToolExecutionMode(StrEnum):
    """Harness-level tool execution posture."""

    DEFAULT = "default"
    READ_ONLY = "read_only"
    BYPASS_APPROVAL = "bypass_approval"
    LOCKED_DOWN = "locked_down"


class ToolPermissionPolicy(BaseModel):
    """Allowlist-based tool execution policy."""

    model_config = ConfigDict(extra="forbid")

    allowed_tools: set[str] = Field(default_factory=set, description="Allowed tool names.")
    denied_tools: set[str] = Field(default_factory=set, description="Tool names denied first.")
    always_allowed_tools: set[str] = Field(
        default_factory=set,
        description="Tool names allowed without approval unless blocked by mode or capability.",
    )
    security_mode: SecurityMode = Field(
        default=SecurityMode.PRIVATE_PROJECT,
        description="Security mode used for tool execution decisions.",
    )
    mode: ToolExecutionMode = Field(
        default=ToolExecutionMode.DEFAULT,
        description="Harness tool execution posture.",
    )

    def allows(self, tool_name: str) -> bool:
        """Return whether a tool may execute."""

        return tool_name not in self.denied_tools and (
            tool_name in self.allowed_tools or tool_name in self.always_allowed_tools
        )


class ToolPermission(BaseModel):
    """Fine-grained permission for one tool."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    allow_read: bool = False
    allow_write: bool = False
    allow_network: bool = False
    require_human_approval: bool = True


class ToolCallDecision(BaseModel):
    """Decision outcome for one attempted tool invocation."""

    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str
    required_approval: bool = False
    pipeline: list[str] = Field(default_factory=list, description="Permission pipeline phases.")


def evaluate_tool_call(
    permission: ToolPermission | None,
    *,
    security_mode: SecurityMode = SecurityMode.PRIVATE_PROJECT,
    mode: ToolExecutionMode = ToolExecutionMode.DEFAULT,
    always_allowed: bool = False,
    requires_write: bool = False,
    requires_network: bool = False,
) -> ToolCallDecision:
    """Evaluate one call against explicit capability requirements."""

    pipeline = ["deny_rule"]
    if security_mode is SecurityMode.AIR_GAPPED and requires_network:
        return ToolCallDecision(
            allowed=False,
            reason="air_gapped_blocks_network_tools",
            pipeline=pipeline,
        )
    if mode is ToolExecutionMode.LOCKED_DOWN:
        return ToolCallDecision(allowed=False, reason="locked_down_mode", pipeline=pipeline)
    pipeline.append("tool_check_permission")
    if security_mode in {SecurityMode.ENTERPRISE, SecurityMode.AIR_GAPPED} and permission is None:
        return ToolCallDecision(
            allowed=False,
            reason="explicit_tool_permission_required",
            pipeline=pipeline,
        )
    pipeline.append("bypass_mode")
    if mode is ToolExecutionMode.BYPASS_APPROVAL and not requires_network:
        return ToolCallDecision(allowed=True, reason="bypass_mode_allowed", pipeline=pipeline)
    pipeline.append("always_allow_rule")
    allowed_by_always_rule = (
        always_allowed
        and not requires_network
        and (not requires_write or mode is not ToolExecutionMode.READ_ONLY)
    )
    if allowed_by_always_rule:
        return ToolCallDecision(allowed=True, reason="always_allowed_tool", pipeline=pipeline)
    pipeline.append("read_only_auto_allow")
    if mode is ToolExecutionMode.READ_ONLY and requires_write:
        return ToolCallDecision(allowed=False, reason="read_only_blocks_write", pipeline=pipeline)
    if permission is None:
        if not requires_write and not requires_network:
            return ToolCallDecision(allowed=True, reason="allowed_legacy_policy", pipeline=pipeline)
        return ToolCallDecision(allowed=False, reason="tool_not_allowlisted", pipeline=pipeline)
    pipeline.append("mode_default")
    if requires_write and not permission.allow_write:
        return ToolCallDecision(allowed=False, reason="write_not_allowed", pipeline=pipeline)
    if requires_network and not permission.allow_network:
        return ToolCallDecision(allowed=False, reason="network_not_allowed", pipeline=pipeline)
    return ToolCallDecision(
        allowed=not permission.require_human_approval,
        reason="human_approval_required" if permission.require_human_approval else "allowed",
        required_approval=permission.require_human_approval,
        pipeline=pipeline,
    )
