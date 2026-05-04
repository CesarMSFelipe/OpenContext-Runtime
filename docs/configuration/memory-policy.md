# Memory Policy

## Purpose
Memory policy controls enablement, harvesting, approval, raw storage, classification, retention, and pruning of low-value or expired facts.

## Current Status
Memory config is implemented for local memory enablement, approval requirements, raw-storage
prevention, default classification, retention, and pruning preferences. Automatic harvesting is off
by default, approval is required by default, and stored memory is redacted with provenance metadata.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
