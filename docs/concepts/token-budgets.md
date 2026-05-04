# Token Budgets

## Purpose
Input budgets reserve output tokens first, then allocate section budgets for system, instructions, repo map, memory, retrieved context, conversation, and tools.

## Current Status
Implemented with deterministic token estimation, per-section budgets, output-token reservation,
context-packing enforcement, output modes, and traceable omissions. Budgets apply to prompt sections
such as system, instructions, tool schemas, project manifest, repo map, workflow contract, memory,
retrieved context, conversation, and tool output.

Provider-specific tokenizers can be added outside core later; core intentionally uses a deterministic
local estimator so tests and budget decisions are reproducible.

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
