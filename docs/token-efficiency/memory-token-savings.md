# Memory Token Savings

## Purpose
Progressive memory injects pinned and relevant compact memory only, while omitted and expandable items remain available by id.

## Current Status
Implemented through progressive disclosure memory selection. Pinned and relevant compact memories
are injected first; omitted memories remain available by id for explicit expansion. Search is
multi-signal and traceable, and memory content is redacted before storage.

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
