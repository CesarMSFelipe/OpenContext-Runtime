# Prompt Caching

## Purpose
Cache-aware prompt order keeps stable tool schemas, policy, manifest, repo map, workflow contract, and stable memory before dynamic context.

## Current Status
Implemented as provider-neutral prompt-cache planning and stable section ordering. Exact local cache
interfaces exist; semantic cache and provider explicit cache APIs remain disabled or scaffolded by
default.

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
