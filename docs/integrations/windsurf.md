# Windsurf

## Purpose
Use OpenContext Runtime as the safe context source for Windsurf workspaces, with a workspace rule that asks the agent to request compact, redacted context packs.

## Current Status
Implemented: `opencontext agent init --target windsurf` creates `.windsurf/rules/opencontext.md`.

## Setup
```bash
opencontext onboard
opencontext agent init --target windsurf
opencontext doctor security
opencontext pack . --query "Review authentication" --mode plan --copy
```

The generated rule is intentionally small and contains no secrets or provider credentials.

## Related Commands
```bash
opencontext agent init --target windsurf
opencontext agent-context "Review access control" --target windsurf --copy
opencontext pack . --query "review auth" --copy
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/adapters/agent_manifest.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
- `packages/opencontext_core/opencontext_core/runtime.py`
