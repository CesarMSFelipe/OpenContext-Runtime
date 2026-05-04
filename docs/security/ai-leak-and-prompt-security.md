# Ai Leak And Prompt Security

## Purpose
Prompt/config leaks are assumed. Prompts must not contain secrets, tool schemas should avoid sensitive internals, and release artifacts are scanned for source maps, env files, raw traces, and AI config leaks. Implemented scaffolds live in `opencontext_core.operating_model.ai_leak`.

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
