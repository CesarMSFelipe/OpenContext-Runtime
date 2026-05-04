from __future__ import annotations

from opencontext_core.actions import ActionRequest, ActionType, ApprovalLevel, evaluate_action
from opencontext_core.config import SecurityMode


def test_default_action_policy_allows_reads_and_requires_approval_for_safe_commands() -> None:
    read_decision = evaluate_action(ActionRequest(action=ActionType.READ_CONTEXT))
    test_decision = evaluate_action(ActionRequest(action=ActionType.RUN_TEST))
    approved_test = evaluate_action(ActionRequest(action=ActionType.RUN_TEST, approved=True))

    assert read_decision.allowed is True
    assert read_decision.decision is ApprovalLevel.ALLOW
    assert test_decision.allowed is False
    assert test_decision.requires_approval is True
    assert approved_test.allowed is True


def test_default_action_policy_denies_write_network_mcp_and_unallowlisted_tools() -> None:
    assert evaluate_action(ActionRequest(action=ActionType.WRITE_FILE)).allowed is False
    assert evaluate_action(ActionRequest(action=ActionType.NETWORK)).allowed is False
    assert evaluate_action(ActionRequest(action=ActionType.MCP_TOOL)).allowed is False
    call_tool = evaluate_action(ActionRequest(action=ActionType.CALL_TOOL))

    assert call_tool.reason == "tool_not_allowlisted"


def test_sandboxed_writes_still_require_allowlist_and_approval() -> None:
    pending = evaluate_action(
        ActionRequest(
            action=ActionType.WRITE_FILE,
            sandbox_enabled=True,
            explicitly_allowlisted=True,
        )
    )
    approved = evaluate_action(
        ActionRequest(
            action=ActionType.WRITE_FILE,
            sandbox_enabled=True,
            explicitly_allowlisted=True,
            approved=True,
        )
    )

    assert pending.allowed is False
    assert pending.requires_approval is True
    assert approved.allowed is True


def test_air_gapped_blocks_external_provider_and_raw_exports() -> None:
    external = evaluate_action(
        ActionRequest(
            action=ActionType.CALL_LLM,
            external_provider=True,
            explicitly_allowlisted=True,
        ),
        security_mode=SecurityMode.AIR_GAPPED,
    )
    raw_export = evaluate_action(ActionRequest(action=ActionType.EXPORT_CONTEXT, sanitized=False))

    assert external.reason == "air_gapped_blocks_external_provider"
    assert raw_export.reason == "raw_context_export_denied"
