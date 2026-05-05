# OpenClaw wrapper

OpenClaw can use OpenContext as a preflight context preparation step. The wrapper
prepares context locally, then you provide the resulting markdown to OpenClaw.

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Add error handling to the API endpoints" \
  --output /tmp/opencontext-openclaw.md
```

Use the generated file as the context payload for OpenClaw. This ensures OpenClaw
receives only relevant, security-reviewed context instead of raw repository dumps.

Operational notes:

- Run OpenContext indexing once per session for best performance.
- Use specific, actionable task descriptions for better context selection.
- Monitor token usage in the trace to optimize your `--max-tokens` setting.
- Keep provider calls outside `opencontext_core` to maintain separation of concerns.