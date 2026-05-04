# Pinned Memory

## Purpose
Pinned memory is always considered for injection, but classification and expiry policy still apply before it reaches a prompt.

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
