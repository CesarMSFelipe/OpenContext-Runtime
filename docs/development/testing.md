# Testing

## Purpose
Run pytest, ruff, ruff format --check, and mypy packages/opencontext_core before handoff.

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
