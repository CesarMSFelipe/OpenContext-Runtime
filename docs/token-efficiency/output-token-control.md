# Output Token Control

## Purpose
OutputBudgetController supports full, concise, technical_terse, structured, patch_only, report, and json modes. technical_terse preserves code, commands, paths, symbols, numbers, warnings, policy decisions, errors, and test results while reducing prose.

## Current Status
Implemented through output policy config, output modes, and output budget control. The controller
reduces low-signal prose while preserving high-value technical elements such as code, commands,
paths, symbols, numbers, warnings, policy decisions, errors, and test results.

## Related Commands
```bash
opencontext tokens report .
opencontext inspect repomap --format toon
opencontext pack . --query "review auth" --format compact_table
opencontext cache plan --query "review auth"
opencontext ask "Summarize project" --output-mode technical_terse
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
- `packages/opencontext_core/opencontext_core/operating_model/performance.py`
