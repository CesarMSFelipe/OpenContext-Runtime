# OpenClaw vs OpenContext: Architecture Boundary

## Purpose split

- **OpenClaw** is an assistant/action layer (agent orchestration, actions, channels, productivity flows).
- **OpenContext Runtime** is a secure context/security layer (indexing, retrieval, context packing, policy enforcement, trace hygiene).

OpenContext should not become an assistant, chat app, channel router, voice application, or productivity agent.

## Imported infrastructure lessons (adapted)

1. `.opencontext/` local workspace:
   - `workflows/`, `plugins/`, `policies/`, `state/`, `cache/`, `traces/`.
2. `opencontext onboard` for local secure bootstrap.
3. `opencontext doctor` and `opencontext doctor security` for baseline posture checks.
4. Plugin manifests with explicit permission grants.
5. ContextEngine lifecycle hooks (`before_run`, `after_run`) for policy extension points.
6. Workflow packs as reusable secure context workflows.
7. Adapter boundary model for Codex/Cursor/Claude Code/OpenClaw integrations.
8. Deny-by-default plugin policy (no network/write/MCP unless allowlisted).
9. Future local-only daemon architecture (not implemented):
   - optional localhost process,
   - no remote control plane,
   - bounded local IPC,
   - policy checks before every context export.

## Security invariants

- No tools enabled by default.
- No MCP enabled by default.
- No external provider enabled by default.
- No raw traces exported by default.
- No secrets in context, cache, memory, or traces.
