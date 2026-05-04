# Model Role Routing

## Purpose
ModelRoleRouter maps classifier, retriever, compressor, generator, critic, and verifier roles to provider/model aliases.

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
