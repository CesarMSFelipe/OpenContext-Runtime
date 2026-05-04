# Claude Code

## Purpose
Use stable, redacted context packs with Claude Code-style terminal workflows. Keep `CLAUDE.md` concise and let OpenContext produce task-specific packs.

## Current Status
Implemented: `opencontext agent init --target claude-code` creates a project-local `CLAUDE.md` with safe OpenContext commands. Provider caching remains policy-scaffolded only.

## Setup
```bash
opencontext onboard
opencontext agent init --target claude-code
opencontext doctor security
opencontext pack . --query "Review authentication" --mode plan --copy
```

In Claude Code, ask it to follow `CLAUDE.md` and use OpenContext packs instead of loading the whole repository.

## Related Commands
```bash
opencontext agent init --target claude-code
opencontext agent-context "Review access control" --target claude-code --copy
opencontext pack . --query "review auth" --copy
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/adapters/agent_manifest.py`
- `packages/opencontext_cli/opencontext_cli/main.py`
- `packages/opencontext_core/opencontext_core/runtime.py`
