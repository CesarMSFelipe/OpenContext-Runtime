# Claude Code wrapper

Claude Code can consume the same prepared context payload. OpenContext remains
the local indexing, packing, redaction, and trace layer.

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Find the runtime path that prepares context for non-CLI adapters" \
  --output /tmp/opencontext-claude-code.md
```

Attach or paste the generated markdown before asking Claude Code to edit or
review files.

Operational notes:

- Use OpenContext before broad repository questions.
- Prefer a narrow task statement over "read the whole project".
- Treat the OpenContext trace id as the audit handle for what was sent.
- Do not place provider credentials in `.opencontext/`, traces, or benchmark
  files.

