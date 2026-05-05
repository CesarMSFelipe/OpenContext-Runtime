# GitHub Copilot wrapper

GitHub Copilot can consume the same prepared context payload. OpenContext remains
the local indexing, packing, redaction, and trace layer.

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Implement user authentication with JWT tokens" \
  --output /tmp/opencontext-copilot.md
```

Paste the generated markdown into your code comments or as context for Copilot Chat.
The prepared context ensures Copilot has relevant, redacted project information without
exposing the entire repository.

Operational notes:

- Use OpenContext before asking Copilot about complex project-specific logic.
- Prefer specific tasks over broad "help me understand this codebase" requests.
- The trace ID allows you to correlate Copilot suggestions with the context provided.
- Keep `.opencontext/` and `.storage/` local to avoid committing sensitive data.