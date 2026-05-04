from __future__ import annotations

import pytest

from opencontext_core.context.assembler import PromptAssembler
from opencontext_core.tools import (
    NativeToolRegistry,
    ToolDefinition,
    ToolExecutionMode,
    ToolPermissionPolicy,
)


def test_tool_registration_denial_allowance_and_prompt_schema() -> None:
    registry = NativeToolRegistry()
    registry.register(
        ToolDefinition(
            name="echo",
            description="Echo arguments.",
            input_schema={"type": "object", "properties": {"value": {"type": "string"}}},
            handler=lambda args: {"value": args["value"]},
        )
    )

    with pytest.raises(PermissionError):
        registry.execute("echo", {"value": "x"}, ToolPermissionPolicy())

    result = registry.execute("echo", {"value": "x"}, ToolPermissionPolicy(allowed_tools={"echo"}))
    prompt = PromptAssembler().assemble("Use tool schema", [], tool_schemas=registry.schema_text())

    assert "untrusted_context" in result["value"]
    assert "x" in result["value"]
    assert registry.calls[-1].allowed is True
    assert registry.calls[-1].sanitized is True
    assert (
        "echo"
        in next(section for section in prompt.sections if section.name == "tool_schemas").content
    )


def test_tool_policy_requires_explicit_permission_in_enterprise() -> None:
    registry = NativeToolRegistry()
    registry.register(
        ToolDefinition(
            name="echo",
            description="Echo arguments.",
            input_schema={"type": "object", "properties": {"value": {"type": "string"}}},
            handler=lambda args: {"value": args["value"]},
        )
    )
    with pytest.raises(PermissionError):
        registry.execute(
            "echo",
            {"value": "x"},
            ToolPermissionPolicy(allowed_tools={"echo"}, security_mode="enterprise"),
        )


def test_air_gapped_blocks_network_tool_calls() -> None:
    registry = NativeToolRegistry()
    registry.register(
        ToolDefinition(
            name="http_fetch",
            description="Fetch URL.",
            input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
            handler=lambda args: {"url": args["url"]},
        )
    )
    with pytest.raises(PermissionError):
        registry.execute(
            "http_fetch",
            {"url": "https://example.com"},
            ToolPermissionPolicy(allowed_tools={"http_fetch"}, security_mode="air_gapped"),
            requires_network=True,
        )


def test_tool_policy_supports_always_allow_and_read_only_mode() -> None:
    registry = NativeToolRegistry()
    registry.register(
        ToolDefinition(
            name="inspect",
            description="Read only inspection.",
            input_schema={"type": "object"},
            handler=lambda args: {"value": "ok"},
        )
    )

    result = registry.execute(
        "inspect",
        {},
        ToolPermissionPolicy(
            always_allowed_tools={"inspect"},
            mode=ToolExecutionMode.READ_ONLY,
        ),
    )

    assert "ok" in result["value"]
    assert registry.calls[-1].allowed is True


def test_read_only_mode_blocks_write_even_when_allowlisted() -> None:
    registry = NativeToolRegistry()
    registry.register(
        ToolDefinition(
            name="edit",
            description="Write file.",
            input_schema={"type": "object"},
            handler=lambda args: {"value": "edited"},
        )
    )

    with pytest.raises(PermissionError):
        registry.execute(
            "edit",
            {},
            ToolPermissionPolicy(
                always_allowed_tools={"edit"},
                mode=ToolExecutionMode.READ_ONLY,
            ),
            requires_write=True,
        )
