# Content Router

## Purpose
ContentRouter chooses code, log, structured, trace, tool output, repo map, and security finding strategies rather than compressing all text the same way.

## Current Status
Implemented in `ContentRouter`. The router detects code, logs, JSON, YAML, Markdown, traces, tool
output, memory facts, repo maps, security findings, workflows, plain text, and unknown content. Each
route selects a compression strategy, serialization format, protected span categories, security
policy, and untrusted-content handling.

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
