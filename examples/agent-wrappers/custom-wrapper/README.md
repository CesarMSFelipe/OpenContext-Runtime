# Custom Agent Wrapper

This example shows how to build a custom agent integration using the OpenContext runtime-first pattern. The wrapper can be adapted for any agent that needs compact, redacted context.

## Usage

```bash
pip install opencontext-core
python examples/agent-wrappers/prepare_context.py \
  --root . \
  --task "Review the authentication implementation and suggest improvements" \
  --output /tmp/opencontext-context.md
```

## Integration Script

Uses the shared `prepare_context.py` script from the parent directory.

1. **Runtime initialization** - Create the OpenContext runtime
2. **Project setup** - Index the project on first run
3. **Context preparation** - Pack relevant context for a task
4. **Output generation** - Write a payload for the agent

## Minimal Python Example

```python
from opencontext_core import OpenContextRuntime

runtime = OpenContextRuntime()
runtime.setup_project("/path/to/project")

# Prepare context for a specific task
prepared = runtime.prepare_context(
    "Review authentication implementation",
    max_tokens=4000,
    mode="review"
)

# Use the prepared context with your agent
agent_input = {
    "task": "Review authentication implementation",
    "context": prepared.context,
    "sources": prepared.included_sources,
    "trace_id": prepared.trace_id,
}
```

## Operational Notes

- Run `setup_project()` once per session for best performance
- Use `--max-tokens` aligned with your target model's capabilities
- Store `trace_id` for audit trails and context reconstruction
- Keep provider calls outside `opencontext_core` for separation of concerns