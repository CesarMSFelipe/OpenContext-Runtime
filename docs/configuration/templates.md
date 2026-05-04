# Templates

## Purpose
Templates are safe overlays for generic, drupal, symfony, python, node, typescript, enterprise, air-gapped, and ci workflows. They do not enable external providers or tools silently.

## Current Status
Implemented as reusable YAML overlays in `configs/` and generated setup defaults. Templates keep
external providers, native tools, MCP execution, raw traces, and automatic harvesting off unless the
template explicitly documents a policy change. Stack templates provide hints without importing stack
frameworks into core.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
