# Measuring Savings

## Purpose
Measure raw repository tokens, repo map tokens, context pack tokens, output mode, markdown vs compact serialization, memory injected/omitted tokens, compression savings, and quality risk.

| Scenario | Raw Tokens | Final Input Tokens | Output Budget | Format | Memory Tokens | Savings % | Quality Risk |
|---|---:|---:|---:|---|---:|---:|---|
| Local proof | TBD | TBD | concise | markdown/toon | TBD | TBD | reported |

## Current Status
Implemented through token reports, context pack token accounting, trace token estimates, output
budget reports, compact serializers, and ContextBench source-coverage checks. Provider-side cache
estimates are planning data only unless a host adapter explicitly enables provider cache APIs.

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
