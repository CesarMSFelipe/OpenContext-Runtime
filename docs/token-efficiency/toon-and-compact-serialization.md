# Compact Serialization

## Purpose
Compact table serializers reduce structured metadata tokens. Source code blocks that require formatting should stay markdown/code.

## Current Status
Implemented through deterministic serializers for Markdown, JSON, YAML, structured output,
and compact tables. These formats are for structured metadata, reports, traces, repo maps, and
context accounting; source code that needs exact formatting stays in Markdown/code blocks.

## Related Commands
```bash
opencontext tokens report .
opencontext inspect repomap --format compact
opencontext pack . --query "review auth" --format compact_table
opencontext cache plan --query "review auth"
opencontext ask "Summarize project" --output-mode technical_terse
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
- `packages/opencontext_core/opencontext_core/operating_model/performance.py`
