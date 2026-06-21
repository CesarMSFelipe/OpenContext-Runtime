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
- `packages/opencontext_core/opencontext_core/memory_usability/serializers.py` — `ContextSerializer` / `SerializationFormat`, the serializer surface to extend
- `tests/core/`
