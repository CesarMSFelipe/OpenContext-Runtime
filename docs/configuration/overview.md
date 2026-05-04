# Overview

## Purpose
Configuration is safe by default and deep-merged onto built-in defaults. Most users should run `opencontext onboard` and avoid manual YAML until they need provider, memory, output, or workflow customization.

## Current Status
Config models are implemented in `packages/opencontext_core/opencontext_core/config.py` and loaded
through `load_config()`, which deep-merges project YAML onto safe defaults. Security, provider,
tool, memory, cache, output, retrieval, context packing, embeddings, workflow, server, egress,
latency, and context-layer policies are represented explicitly.

Some fields are active runtime controls today; others are policy scaffolds for future adapters. The
defaults are still the important contract: external providers, native tools, MCP execution, network
egress, raw traces, semantic cache, and automatic memory harvesting are off unless policy enables
them.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
