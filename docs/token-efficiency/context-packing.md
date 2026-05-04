# Context Packing

## Purpose
Packing ranks candidates by priority, score, token density, and trust, then records omission reasons for traceability.

## Current Status
Implemented in `ContextPackBuilder`. The packer orders candidates by priority, score, value per
token, source trust, and stable id. It records included and omitted items, used tokens, available
tokens, value-per-token metadata, source-trust metadata, and explicit omission reasons.

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
