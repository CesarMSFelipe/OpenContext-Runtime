# Overview

## Purpose
Profiles keep framework-specific knowledge outside core.

## Current Status
First-party profile registry exists in `packages/opencontext_profiles`. CLI templates can select profile names.

OpenContext ships 230+ first-party stack profiles — see the full list in [Technology Profiles](../architecture/technology-profiles.md). The pages here cover the most common ones.

## Related Commands
```bash
opencontext init --template drupal
opencontext init --template python
opencontext init --template node
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/project/profiles.py`
- `packages/opencontext_profiles/opencontext_profiles/`
