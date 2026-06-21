# Performance

The performance pages cover the cost, cache, latency, and model-routing
mechanisms in the operating model. Each page documents one mechanism; the
shared status and command surface live here.

## Current Status
Implemented as local deterministic scaffolds; provider-specific cache and cost
integrations are future adapters outside core.

## Related Commands
```bash
opencontext cache plan --query "review auth"
opencontext cache warm --workflow code-review
opencontext report cost
opencontext harness run --workflow explore-only --task "security audit"
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/performance.py`

## Pages
- [Batch Runs](batch-runs.md)
- [Cache Aware Prompting](cache-aware-prompting.md)
- [Cache Warming](cache-warming.md)
- [Context Layers](context-layers.md)
- [Cost Ledger](cost-ledger.md)
- [Latency Budgets](latency-budgets.md)
- [Model Escalation](model-escalation.md)
- [Model Role Routing](model-role-routing.md)
- [Offline Precomputation](offline-precomputation.md)
- [Provider Context Caching](provider-context-caching.md)
