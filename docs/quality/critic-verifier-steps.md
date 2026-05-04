# Critic Verifier Steps

## Purpose
Critic and verifier steps are cheap deterministic scaffolds today and future model-role workflow nodes later.

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
