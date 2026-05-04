# Optional CLI Installation

The CLI is a convenience adapter, not the required runtime path. Install it when a user or team
wants explicit `opencontext` commands for local diagnosis, context packs, memory operations, or
release checks.

Use the CLI when the human operator wants terminal control. Use the runtime/API path when an IDE,
agent wrapper, service, or product should hide OpenContext-specific commands from the end user.

```bash
python3 -m pip install opencontext-cli
```

Typical CLI setup:

```bash
opencontext onboard
opencontext index .
opencontext pack . --query "Review authentication" --mode plan --copy
```

The commands map directly to the runtime-first APIs:

| CLI command | Runtime/API equivalent |
| --- | --- |
| `opencontext onboard` | `runtime.setup_project(...)` or `POST /v1/setup` |
| `opencontext index .` | `runtime.index_project(...)` |
| `opencontext pack . --query ...` | `runtime.prepare_context(...)` or `POST /v1/context` |
| `opencontext trace last` | `runtime.latest_trace()` |

Use the CLI for:

- Manual onboarding and doctor checks.
- One-off context packs copied into agent sessions.
- Local memory commands.
- Release, prompt, token, and evidence reports.

The CLI should not be required for product integrations. If users must run `opencontext` before
the integration works, prefer moving that setup into the host application through `setup_project()`.
