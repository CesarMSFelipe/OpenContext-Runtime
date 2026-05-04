# Context Quality Evaluation

## Purpose
Context quality evaluation should check source coverage, noise, critical missing sources, compression risk, and citation support.

## Current Status
Implemented locally for context packs and traces with deterministic source count, token coverage, omitted-token, over-budget, and risk reporting. Critical-source coverage, citation support, and critic/verifier model calls are future workflow adapters.

## Related Commands
```bash
opencontext quality preflight --query "review auth"
opencontext quality verify last
opencontext report quality
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/quality.py`
- `packages/opencontext_core/opencontext_core/evaluation/context_quality.py`
