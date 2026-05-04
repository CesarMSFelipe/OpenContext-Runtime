# Workflow Config

## Purpose
Workflows are named ordered steps. Current execution supports the code_assistant path; many team workflows are scaffolded for repeatable policy and token planning.

## Current Status
Implemented for named ordered workflow steps loaded from config. `code_assistant`, `sdd`, and
`sdd_apply` paths are represented in defaults. Step execution is explicit through the workflow
registry, and unknown workflow names or step names fail closed. Controlled harness planning exists
separately for agentic turn preflight.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
