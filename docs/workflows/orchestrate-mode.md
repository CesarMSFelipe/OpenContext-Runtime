# Orchestrate Mode

## Purpose
Orchestrate mode is scaffolded around plan, context_pack, approval_gate, validation, and report steps. It does not execute unsafe actions by default.

## Current Status
Core `code_assistant` execution is implemented. Many team workflow commands are honest scaffolds that print policy and token plans without provider/tool calls.

## Related Commands
```bash
opencontext workflows list
opencontext workflow dry-run security-audit
opencontext run architect --task "review architecture"
opencontext propose patch --task "fix tests"
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/workflow/`
- `packages/opencontext_cli/opencontext_cli/main.py`
