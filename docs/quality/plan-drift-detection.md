# Plan Drift Detection

## Purpose
PlanDriftDetector compares approved plan intent with attempted action and blocks unexpected external egress.

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
