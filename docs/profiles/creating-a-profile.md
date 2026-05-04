# Creating A Profile

## Purpose
Create profiles by extending `TechnologyProfile` outside core and keeping framework imports in profile packages.

## Current Status
First-party profile registry exists in `packages/opencontext_profiles`. CLI templates can select profile names.

## Related Commands
```bash
opencontext init --template drupal
opencontext init --template python
opencontext validate --profile drupal
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/project/profiles.py`
- `packages/opencontext_profiles/opencontext_profiles/`
