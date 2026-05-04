# Defaults

## Purpose
Defaults use `private_project`, mock provider, external providers off, tools off, MCP off, raw traces off, exact cache on, semantic cache off, memory on with harvest disabled, and concise output capped at 1500 tokens.

## Current Status
Implemented in `default_config_data()` and deep-merged by `load_config()`. Defaults are intentionally
usable without keys: mock provider, local indexing, local traces, exact local cache, memory enabled
but harvest disabled, concise output, external providers off, tools off, MCP off, network denied, raw
trace context off, semantic cache off, and provider explicit cache APIs off.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
