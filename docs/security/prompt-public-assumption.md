# Prompt Public Assumption

## Purpose
If a prompt cannot safely become public, it should not contain that content. Use `opencontext prompt audit` and `opencontext prompt export --public-safe`.

## Current Status
Implemented where linked below; broader enterprise controls remain scaffolded and fail closed by default.

## Related Commands
```bash
opencontext doctor security
opencontext security scan .
opencontext prompt audit .
opencontext release audit --dist dist/
opencontext provider simulate --provider openai --classification confidential
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/safety/`
- `packages/opencontext_core/opencontext_core/operating_model/ai_leak.py`
