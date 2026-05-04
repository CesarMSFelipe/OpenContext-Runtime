# Tool Policy

## Purpose
Tool and MCP policy is deny-by-default. Future tool adapters must declare read, write, network, classification access, egress risk, approvals, and output limits.

## Current Status
Tool config and permission policy models are implemented. Native tools and MCP execution are off by
default. The policy layer supports allowed tools, denied tools, always-allowed read-only tools,
execution modes, write/network capability checks, and human approval requirements. Tool outputs are
sanitized and wrapped as untrusted context when the registry is used.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
