# Cursor

## Purpose
Use OpenContext packs as redacted project evidence for Cursor and keep workspace rules focused on safe context gathering.

## Current Status
Implemented: `opencontext agent init --target cursor` creates `.cursor/rules/opencontext.mdc`.

## Setup
```bash
opencontext onboard
opencontext agent init --target cursor
opencontext doctor security
opencontext pack . --query "Review authentication" --mode plan --copy
```

The generated rule tells Cursor to prefer `opencontext pack` and `opencontext agent-context` over whole-repository prompts.

## Related Commands
```bash
opencontext agent init --target cursor
opencontext agent-context "Review access control" --target cursor --copy
opencontext pack . --query "review auth" --copy
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/adapters/agent_manifest.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
- `packages/opencontext_core/opencontext_core/runtime.py`
