# OpenCode And Kilo Code

## Purpose
OpenCode and Kilo Code can consume generated context packs, `AGENTS.md` instructions, and agent-context blocks.

## Current Status
Implemented:

- `opencontext agent init --target opencode` creates `AGENTS.md` and `opencode.json`.
- `opencontext agent init --target kilo-code` creates `AGENTS.md`.

## Setup
```bash
opencontext onboard
opencontext agent init --target opencode
opencontext doctor security
opencontext pack . --query "Review authentication" --mode plan --copy
```

For Kilo Code:

```bash
opencontext agent init --target kilo-code
opencontext agent-context "Review access control" --target kilo-code --copy
```

## Related Commands
```bash
opencontext agent init --target opencode
opencontext agent init --target kilo-code
opencontext agent-context "Review access control" --target opencode --copy
opencontext pack . --query "review auth" --copy
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/adapters/agent_manifest.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
- `packages/opencontext_core/opencontext_core/runtime.py`
