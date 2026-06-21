# Technology Profiles

## Purpose
Technology profiles supply stack-specific ignores and workflow hints without importing frameworks into core. Drupal, Symfony, Python, Node, and TypeScript are profile/template paths.

## Current Status
Implemented as a boundary above core. `opencontext_core` defines profile interfaces and generic
fallback behavior; first-party profile hints and templates live in `opencontext_profiles` and
`configs/`. Profiles can influence ignores, file classification, symbol extraction hints, workflow
suggestions, and validation commands without importing Drupal, Symfony, Python, Node, or TypeScript
framework code into core.

## Related Commands
```bash
opencontext index .
opencontext inspect repomap
opencontext pack . --query "review auth"
opencontext doctor tokens
```

## Implemented Code
- `packages/opencontext_profiles/opencontext_profiles/` (registry.py, markers.py, standards.py)
- `packages/opencontext_core/opencontext_core/project/profiles.py` (profile interface)
- `configs/` (per-stack YAMLs: opencontext.drupal.yaml, opencontext.symfony.yaml, opencontext.python.yaml, opencontext.node.yaml)
