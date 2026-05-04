# Tool Chain Analysis

## Purpose
ToolChainAnalyzer detects risky sequences such as read_secret to external_network and llm_output to shell_command.

## Current Status
Local deterministic gates are implemented. Critic/verifier model calls are future workflow adapters.

## Related Commands
```bash
opencontext quality preflight --query "review auth"
opencontext quality verify last
opencontext report quality
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/quality.py`
