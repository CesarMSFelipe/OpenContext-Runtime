# Air Gapped

## Purpose
Air-gapped mode blocks external providers, MCP, and telemetry and should be paired with local mock/local providers.

## Current Status
Design and local scaffolds are present. Do not treat the project as a fully certified enterprise platform yet.

## Related Commands
```bash
opencontext governance report
opencontext evidence pack
opencontext org baseline check
opencontext run receipt last
opencontext release gate
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/`
- `packages/opencontext_core/opencontext_core/safety/`
