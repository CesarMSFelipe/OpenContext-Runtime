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
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/indexing/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
