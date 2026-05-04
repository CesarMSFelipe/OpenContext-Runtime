# What Is Context Engineering

## Purpose
OpenContext treats context as a compiled artifact: selected, ranked, redacted, packed, serialized, budgeted, and traced. The runtime asks what the safest minimal evidence is for a task before a model is called.

## Current Status
Implemented as a local runtime flow: index the repository, retrieve relevant candidates, rank and
pack context under budget, redact unsafe content, assemble prompt sections, persist traces, and
optionally reuse approved memory. Provider calls, tools, and MCP execution remain policy-gated.

The simplest user-facing outcome is a context pack: compact evidence for one task, with source refs,
token accounting, omission reasons, safety warnings, and a trace id.

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
