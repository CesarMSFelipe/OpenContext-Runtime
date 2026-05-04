# Context Dag

## Purpose
ContextDAG scaffolds raw event nodes, summary nodes, parent-child links, source spans, expansion refs, and quality checks for traceable compression.

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
