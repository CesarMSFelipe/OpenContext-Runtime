# Patch Proposals

## Purpose
Patch proposals are proposal-only scaffolds and do not write files without explicit future approval and sandbox policy.

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
