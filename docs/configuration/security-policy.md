# Security Policy

## Purpose
Security policy controls mode, fail-closed behavior, default classification, provider egress, trace storage, and action permissions.

## Current Status
Implemented for runtime mode, fail-closed behavior, default classification, provider egress,
provider policy checks, trace storage defaults, tool/MCP defaults, and air-gapped blocking. Security
policy is enforced by config loading, provider policy, context firewall checks, sink redaction, trace
sanitization, permission evaluation, and CLI/API guardrails.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
