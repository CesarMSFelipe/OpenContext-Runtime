# Cache Policy

## Purpose
Exact local cache is enabled. Semantic cache and provider explicit cache APIs are disabled by default and represented as provider-neutral policy scaffolds.

## Current Status
Exact local cache, cache-aware prompt planning, MCP response compression policy, semantic cache
policy, and provider-cache policy are represented. Semantic cache and provider explicit cache APIs
remain disabled by default; provider cache settings are planning controls unless a host adapter
implements them.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
