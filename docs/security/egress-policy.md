# Egress Policy

## Purpose
Default egress denies network and webhooks, asks for external URLs, and allows clipboard/file export only after redaction.

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
