# Memory

## Purpose
Memory uses progressive disclosure: pinned context, compact summaries, searchable facts, and expandable original sources. Harvesting is off by default and approval-gated.

## Current Status
Implemented as a local, redacted, provenance-backed context repository plus progressive disclosure
selection. Search uses deterministic multi-signal scoring: keyword overlap, entity-like metadata,
priority, recency, pinned state, and agent-generated facts. Temporal memory, context DAG references,
pinning, expansion, harvesting, novelty checks, compression quality checks, and garbage collection
scaffolds are present.

Automatic harvesting remains disabled by default, harvested memories require approval by default,
and raw trace storage is not used for memory.

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
