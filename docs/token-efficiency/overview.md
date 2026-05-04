# Overview

## Purpose
Token efficiency starts with repo maps, symbol retrieval, context packing, adaptive compression, compact serialization, output budgets, cache-aware prompt order, and memory reuse.

## Current Status
Implemented for deterministic reports, local serializers, context packing, output budget control,
progressive memory, MCP response compression boundaries, and cache-aware prompt planning.
Provider-side explicit cache APIs are scaffolded only.

## Implemented Mechanisms

- Repo-map-first loading: paths, symbols, dependencies, and summaries before raw snippets.
- Deterministic retrieval and ranking with source trust, priority, relevance, and token efficiency.
- Hard context packing budgets with traceable omission reasons.
- Content routing for code, logs, JSON, YAML, trace, tool output, repo maps, memory facts, and
  security findings.
- Adaptive compression with protected spans and compression quality gates.
- Compact serializers for markdown, JSON, YAML, TOON-like structured output, and compact tables.
- Progressive disclosure memory with expandable source ids instead of whole-memory dumps.
- Output modes and output token caps for concise, terse, technical, and report-style responses.
- Cache-aware prompt prefix planning for stable sections such as tool schemas, system policy,
  project manifest, repo maps, and workflow contracts.

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
