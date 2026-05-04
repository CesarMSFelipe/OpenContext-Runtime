"""Permission engine with allow/ask/deny decisions."""

from __future__ import annotations

from opencontext_core.compat import StrEnum
from opencontext_core.config import SecurityMode


class PermissionDecision(StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


RISKY_SCOPES = {
    "context.trace_raw",
    "prompt.send_external",
    "mcp.enable",
    "server.remote_bind",
}


def evaluate_permission(
    scope: str, mode: SecurityMode, explicit_allow: bool = False
) -> PermissionDecision:
    """Return policy decision for a given scope and security mode."""

    if mode is SecurityMode.AIR_GAPPED and scope in {
        "prompt.send_external",
        "mcp.enable",
        "server.remote_bind",
    }:
        return PermissionDecision.DENY
    if scope in RISKY_SCOPES and not explicit_allow:
        return PermissionDecision.ASK
    if explicit_allow:
        return PermissionDecision.ALLOW
    return PermissionDecision.DENY
