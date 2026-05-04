# Workflow Packs

## Purpose
Workflow packs live under `workflow-packs/` and remain policy-governed. External packs cannot silently weaken security defaults.

## Current Status
Core `code_assistant` execution is implemented. Local HMAC integrity signing exists for workflow pack directories with `opencontext packs sign` and `opencontext packs verify`. Public-key signing, transparency logs, and external trust roots are scaffolded.

## Related Commands
```bash
opencontext workflows list
opencontext packs sign code-review --key "$OPENCONTEXT_PACK_SIGNING_KEY"
opencontext packs verify code-review --key "$OPENCONTEXT_PACK_SIGNING_KEY"
opencontext workflow dry-run security-audit
opencontext run architect --task "review architecture"
opencontext propose patch --task "fix tests"
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/workflow/`
- `packages/opencontext_core/opencontext_core/workflow_packs/signing.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
