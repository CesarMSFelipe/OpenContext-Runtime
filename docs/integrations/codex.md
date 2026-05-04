# Codex

## Purpose
Use `opencontext pack --copy` or `opencontext agent-context --target codex` to feed safe context into Codex.

## Current Status
CLI/API/local SDK paths are implemented. Agent-specific integrations are documented patterns unless a command explicitly exists.

## Related Commands
```bash
opencontext agent-context "Review access control" --target codex --copy
opencontext pack . --query "review auth" --copy
opencontext ddev init
```

## Implemented Code
- `packages/opencontext_cli/opencontext_cli/main.py`
- `packages/opencontext_api/opencontext_api/main.py`
- `packages/opencontext_core/opencontext_core/runtime.py`
