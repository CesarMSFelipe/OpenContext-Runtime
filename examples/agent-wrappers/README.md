# Agent wrapper examples

These examples show the intended integration pattern:

1. OpenContext indexes the local repository.
2. OpenContext prepares a compact, redacted context bundle for the task.
3. The agent receives the task plus the prepared context.
4. The agent/provider call remains outside `opencontext_core`.

The examples do not call provider APIs. They are adapter skeletons that keep the
runtime provider-neutral and make cost/security controls visible.

## Generic context preparation

```bash
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Review the authentication flow" \
  --output /tmp/opencontext-agent-context.md
```

The output file is the payload to paste into, pipe into, or attach to an agent.
It contains only the selected context pack, not the full repository.

## Provider-specific usage

- [Codex](codex/README.md)
- [Claude Code](claude-code/README.md)
- [OpenCode](opencode/README.md)
- [GitHub Copilot](copilot/README.md)
- [OpenClaw](openclaw/README.md)
- [Custom Wrapper](custom-wrapper/README.md)

## Python SDK usage

For direct Python integration without CLI:

```python
from opencontext_core import OpenContextRuntime

runtime = OpenContextRuntime()
runtime.setup_project("/path/to/project")

prepared = runtime.prepare_context(
    "Explain the auth module",
    max_tokens=4000,
    mode="review"
)

# Use with any agent
agent_prompt = f"""
Task: Explain the auth module
Context: {prepared.context}
Sources: {prepared.included_sources}
Trace: {prepared.trace_id}
"""
```
- [Custom Wrapper](custom-wrapper/README.md)

