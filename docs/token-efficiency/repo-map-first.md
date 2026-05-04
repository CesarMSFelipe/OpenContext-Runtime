# Repo Map First

## Purpose
Repo map first means the model sees paths and symbols before raw file snippets, reducing prompt volume and improving retrieval precision.

## Current Status
Implemented through project indexing, symbol extraction, dependency graph metadata, repo-map
rendering, and prompt-cache planning. Repo maps are stable, compact prompt sections and do not
include raw source content.

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
