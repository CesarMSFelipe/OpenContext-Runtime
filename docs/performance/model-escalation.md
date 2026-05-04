# Model Escalation

## Purpose
Escalation starts with local/deterministic answers, retrieves more context when needed, asks approval for high-value insufficient runs, and only then escalates.

## Current Status
Implemented as local deterministic scaffolds; provider-specific cache and cost integrations are future adapters outside core.

## Related Commands
```bash
opencontext cache plan --query "review auth"
opencontext cache warm --workflow code-review
opencontext cost report
opencontext workflow dry-run security-audit
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/performance.py`
