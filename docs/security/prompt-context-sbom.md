# Prompt Context Sbom

## Purpose
Prompt/context SBOMs are evidence artifacts listing policy hashes, prompt hashes, context pack hashes, memory refs, selected sources, token estimates, and tool schema hashes without raw prompt text.

## Current Status
Implemented locally for sanitized traces via `PromptContextSBOMBuilder` and `opencontext prompt sbom`. Signing, cross-run SBOM aggregation, and organization attestations remain scaffolded.

## Related Commands
```bash
opencontext doctor security
opencontext prompt audit .
opencontext prompt sbom --trace last --output .opencontext/reports/prompt-context-sbom.json
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/evidence.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
