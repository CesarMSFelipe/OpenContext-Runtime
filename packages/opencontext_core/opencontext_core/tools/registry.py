"""Native tool registry with explicit schemas and permission checks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.errors import WorkflowExecutionError
from opencontext_core.safety.prompt_injection import render_untrusted_context
from opencontext_core.safety.redaction import SinkGuard
from opencontext_core.tools.policy import (
    ToolPermission,
    ToolPermissionPolicy,
    evaluate_tool_call,
)

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ToolDefinition(BaseModel):
    """Registered native tool definition."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    name: str = Field(description="Tool name.")
    description: str = Field(description="Human-readable description.")
    input_schema: dict[str, Any] = Field(description="Explicit input schema.")
    handler: ToolHandler = Field(description="Callable handler.")


class ToolCallRecord(BaseModel):
    """Traceable tool call record."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(description="Tool name.")
    allowed: bool = Field(description="Whether execution was allowed.")
    result: dict[str, Any] | None = Field(default=None, description="Tool result.")
    error: str | None = Field(default=None, description="Tool error.")
    sanitized: bool = Field(default=False, description="Whether output was sanitized.")


class NativeToolRegistry:
    """Registry for future MCP-compatible native tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self.calls: list[ToolCallRecord] = []

    def register(self, definition: ToolDefinition) -> None:
        """Register a tool by name."""

        if definition.name in self._tools:
            raise WorkflowExecutionError(f"Tool already registered: {definition.name}")
        self._tools[definition.name] = definition

    def schema_text(self) -> str:
        """Render tool schemas for prompt assembly."""

        if not self._tools:
            return ""
        lines: list[str] = []
        for tool in sorted(self._tools.values(), key=lambda item: item.name):
            lines.append(f"{tool.name}: {tool.description}\nSchema: {tool.input_schema}")
        return "\n\n".join(lines)

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        policy: ToolPermissionPolicy,
        *,
        permission: ToolPermission | None = None,
        requires_write: bool = False,
        requires_network: bool = False,
    ) -> dict[str, Any]:
        """Execute a tool only when allowed by policy."""

        definition = self._tools.get(name)
        if definition is None:
            record = ToolCallRecord(tool_name=name, allowed=False, error="tool_not_registered")
            self.calls.append(record)
            raise WorkflowExecutionError(f"Tool not registered: {name}")
        if not policy.allows(name):
            record = ToolCallRecord(tool_name=name, allowed=False, error="tool_not_allowed")
            self.calls.append(record)
            raise PermissionError(f"Tool execution denied by policy: {name}")
        decision = evaluate_tool_call(
            permission,
            security_mode=policy.security_mode,
            mode=policy.mode,
            always_allowed=name in policy.always_allowed_tools,
            requires_write=requires_write,
            requires_network=requires_network,
        )
        if not decision.allowed:
            record = ToolCallRecord(tool_name=name, allowed=False, error=decision.reason)
            self.calls.append(record)
            raise PermissionError(f"Tool execution denied by capability policy: {decision.reason}")
        result = definition.handler(arguments)
        safe_result = _sanitize_tool_output(name, result)
        self.calls.append(
            ToolCallRecord(tool_name=name, allowed=True, result=safe_result, sanitized=True)
        )
        return safe_result


def _sanitize_tool_output(tool_name: str, value: dict[str, Any]) -> dict[str, Any]:
    guard = SinkGuard()
    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, str):
            redacted, _ = guard.redact(item)
            sanitized[key] = render_untrusted_context(tool_name, "internal", redacted)
        else:
            sanitized[key] = item
    return sanitized
