# Adding A Profile

## Purpose
Profiles should live outside core and expose declarative hints through `TechnologyProfile`.

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
- `packages/opencontext_core/opencontext_core/project/profiles.py` — the `TechnologyProfile` Protocol (profiles.py:90) to implement against
- `packages/opencontext_profiles/opencontext_profiles/markers.py` — author the new profile class (subclass `MarkerTechnologyProfile`)
- `packages/opencontext_profiles/opencontext_profiles/registry.py` — register it in `first_party_profiles()`
- `tests/core/`
