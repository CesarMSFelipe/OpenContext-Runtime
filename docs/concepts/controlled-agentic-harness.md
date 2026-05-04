# Controlled Agentic Harness

## Purpose
The controlled harness is scaffolded around deny-by-default actions, explicit approval, plan drift checks, and tool-chain analysis. Native tool execution remains disabled by default.

The core planner models each turn before execution: preprocessing, model streaming, error recovery, tool execution, and continuation check. It can trigger compaction from token-ratio thresholds, stop at maximum turn limits, and evaluate proposed tool calls against the same read/write/network permission model used by the native tool registry.

## Current Status
Implemented as a preflight planner, not as unrestricted tool execution. The planner decides whether
a turn may continue, whether compaction is required, and how proposed tool calls should be handled
under deny rules, allowlists, always-allow rules, read-only mode, bypass mode, write/network
capabilities, and human approval requirements.

Native execution is still disabled by default. The planner exists so future harnesses can make
permission and token decisions before any action is taken.

## Related Commands
```bash
opencontext index .
opencontext inspect repomap
opencontext pack . --query "review auth"
opencontext doctor tokens
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/indexing/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
- `packages/opencontext_core/opencontext_core/workflow/harness.py`
- `packages/opencontext_core/opencontext_core/tools/policy.py`
