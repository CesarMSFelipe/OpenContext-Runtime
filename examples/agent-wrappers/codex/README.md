# Codex wrapper

Codex can use OpenContext as a preflight context step. The wrapper prepares the
context locally, then you provide the resulting markdown to Codex with the task.

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Review the API context endpoint and suggest safe changes" \
  --output /tmp/opencontext-codex.md
```

Use the generated file as the context payload for Codex. Keep the task specific:
OpenContext performs best when the query names the area, behavior, or risk being
worked on.

Operational notes:

- Do not send the full repository when a prepared context pack exists.
- Keep `.opencontext/` and `.storage/` local.
- Use lower-cost models for planning and review when the prepared context is
small; escalate only when the trace shows broad or high-risk context.
- Keep provider calls outside `opencontext_core`.

