# Architecture

## Purpose
Core is provider/framework agnostic. API and CLI are thin adapters. Technology profiles live outside core. Safety, ranking, packing, prompt assembly, memory usability, and traces are core interfaces or deterministic implementations.

## Current Status
Implemented around a strict boundary: `opencontext_core` owns domain logic and deterministic local
runtime behavior; API, CLI, profiles, and provider adapters sit above it. Core includes indexing,
repo maps, dependency graphs, retrieval, ranking, packing, compression, prompt assembly, safety,
memory usability, traces, workflows, controlled harness planning, and provider-neutral interfaces.

FastAPI, CLI behavior, provider SDKs, framework-specific profiles, and external storage adapters do
not belong in core.

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
