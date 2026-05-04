# Adding A Serializer

## Purpose
Serializers must be deterministic, redacted, and avoid compacting source code that needs exact formatting.

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
