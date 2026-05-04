from opencontext_core.config import SecurityMode
from opencontext_core.security.permissions import PermissionDecision, evaluate_permission


def test_permission_engine_allow_ask_deny() -> None:
    assert (
        evaluate_permission("context.read", SecurityMode.PRIVATE_PROJECT) is PermissionDecision.DENY
    )
    assert evaluate_permission("mcp.enable", SecurityMode.PRIVATE_PROJECT) is PermissionDecision.ASK
    assert (
        evaluate_permission("provider.mock", SecurityMode.PRIVATE_PROJECT, explicit_allow=True)
        is PermissionDecision.ALLOW
    )


def test_air_gapped_blocks_external_scopes() -> None:
    assert (
        evaluate_permission("prompt.send_external", SecurityMode.AIR_GAPPED)
        is PermissionDecision.DENY
    )
