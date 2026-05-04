# OpenCode wrapper

OpenCode and OpenCode-compatible agents can use the generic prepared context
payload without a custom provider SDK.

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Inspect token-budget enforcement and propose a minimal patch" \
  --output /tmp/opencontext-opencode.md
```

Provide the generated markdown to the agent and keep the actual provider call in
the agent layer.

Operational notes:

- Run OpenContext from the repository root.
- Keep `--max-tokens` aligned with the target model and expected task size.
- Use the included source list to verify that the agent is working from the
  intended files.
- If expected files are missing, add or adjust a ContextBench case before using
  the result for release claims.

