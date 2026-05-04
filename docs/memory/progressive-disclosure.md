# Progressive Disclosure

## Purpose
Layer 0 pinned memory and compact summaries are considered first. Searchable facts and expandable sources are used only when relevant and policy allows.

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
