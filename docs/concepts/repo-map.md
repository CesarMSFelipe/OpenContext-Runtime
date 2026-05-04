# Repo Map

## Purpose
Repo maps summarize paths and symbols before raw file context. Static dependency graphs add source-to-target relationships so retrieval can choose related files without dumping the whole repository.

## Current Status
Implemented: indexing now builds a lightweight deterministic dependency graph for Python, JavaScript/TypeScript, and PHP import/include patterns. Parser-backed language graphs are future work.

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
- `packages/opencontext_core/opencontext_core/indexing/dependency_graph.py`
- `packages/opencontext_core/opencontext_core/memory_usability/`
