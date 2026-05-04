# Compression

## Purpose
Compression is a pipeline with protected spans and quality gates. OpenContext does not claim lossless compression unless source expansion or reconstruction exists.

## Current Status
Implemented for deterministic context compression, protected span preservation, adaptive policy
selection, compression quality checks, and MCP response compression boundaries. Compression remains
conservative for code, security findings, exact snippets, and protected spans.

## Related Commands
```bash
opencontext tokens report .
opencontext inspect repomap --format toon
opencontext pack . --query "review auth" --format compact_table
opencontext cache plan --query "review auth"
opencontext ask "Summarize project" --output-mode technical_terse
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
- `packages/opencontext_core/opencontext_core/operating_model/performance.py`
