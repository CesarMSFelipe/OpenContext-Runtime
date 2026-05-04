# Output Budgets

## Purpose
Output budgets cap generated responses and choose output modes such as concise, technical_terse, patch_only, report, structured, and json.

## Current Status
Implemented through `OutputBudgetController`, output policy config, CLI output modes, and
output-preservation rules. Concise modes reduce prose while preserving code, commands, paths,
symbols, warnings, numbers, policy decisions, errors, and test results.

Output controls complement input context packing: OpenContext budgets what the model sees and also
limits how much downstream output is encouraged or exported.

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
