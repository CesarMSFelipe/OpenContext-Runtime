# Adding A Command

## Purpose
CLI commands should be thin adapters over core services or honest scaffolds that state safety limits.

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
