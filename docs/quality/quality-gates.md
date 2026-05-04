# Quality Gates

## Purpose
PreLLMQualityGate blocks runs before spending tokens when provider policy, source coverage, or token budget fails. PostLLMQualityGate scans output for leaks and budget drift.

## Current Status
Local deterministic gates are implemented. Critic/verifier model calls are future workflow adapters.

## Related Commands
```bash
opencontext quality preflight --query "review auth"
opencontext quality verify last
opencontext report quality
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/quality.py`
