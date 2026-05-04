# Adding A Memory Backend

## Purpose
Memory backends must preserve classification, provenance, token estimates, redaction, expiry, and pruning metadata.

## Current Status
Development workflows are local and test-driven.

## Related Commands
```bash
pytest
ruff check .
ruff format --check .
mypy packages/opencontext_core
```

## Implemented Code
- `packages/opencontext_core/`
- `packages/opencontext_cli/`
- `tests/core/`
