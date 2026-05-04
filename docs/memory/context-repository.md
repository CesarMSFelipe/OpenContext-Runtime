# Context Repository

## Purpose
The context repository lives at `.opencontext/context-repository/` with system, memory, archive, facts, decisions, and summaries collections. Items use frontmatter with id, kind, classification, priority, source, validity, tokens, and pruning metadata.

Search returns traceable scores rather than opaque matches. Each result records matched terms, matched entity-like tokens, a fused score, and a reason string so prompt packing and later audits can explain why a memory was selected.

## Current Status
The local repository, progressive selection, harvesting, novelty gate, pinning, expansion, temporal graph, DAG scaffold, compressor, and GC scaffold are implemented in `memory_usability`.

## Related Commands
```bash
opencontext memory init
opencontext memory list
opencontext memory search "access control"
opencontext memory harvest --from-trace last
opencontext memory prune
opencontext memory facts
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/memory_usability/`
