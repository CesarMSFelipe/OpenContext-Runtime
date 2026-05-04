# Tool Security

## Purpose
Native tools and MCP are disabled by default. Future tools must declare read/write/network flags, classification access, egress risk, approval policy, and token output limits.

## Current Status
Implemented where linked below; broader enterprise controls remain scaffolded and fail closed by default.

Tool decisions follow an explicit pipeline: deny rule, tool permission check, bypass mode, always-allow rule, read-only auto-allow, and mode default. The pipeline is recorded on decisions so harness traces can explain why a tool was allowed, denied, or routed to human approval.

## Related Commands
```bash
opencontext doctor security
opencontext security scan .
opencontext prompt audit .
opencontext release audit --dist dist/
opencontext provider simulate --provider openai --classification confidential
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/safety/`
- `packages/opencontext_core/opencontext_core/operating_model/ai_leak.py`
- `packages/opencontext_core/opencontext_core/tools/policy.py`
- `packages/opencontext_core/opencontext_core/workflow/harness.py`
