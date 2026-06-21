# Air Gapped

## Purpose
Air-gapped mode blocks external providers, MCP, and telemetry, and is enforced in runtime config validation. Pair it with local mock/local providers.

## Current Status
Implemented where linked below; broader enterprise controls remain scaffolded and fail closed by default. Do not treat the project as a fully certified enterprise platform yet.

## Related Commands
```bash
opencontext doctor security
opencontext security scan .
opencontext prompt audit .
opencontext provider simulate --provider openai --classification confidential
opencontext release audit --dist dist/
opencontext release evidence
opencontext release gate
opencontext org baseline check
opencontext report security
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/safety/`
- `packages/opencontext_core/opencontext_core/operating_model/`
- `packages/opencontext_core/opencontext_core/operating_model/ai_leak.py`
