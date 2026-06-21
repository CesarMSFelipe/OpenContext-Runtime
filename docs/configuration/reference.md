# Configuration Reference

This reference documents the top-level OpenContext configuration fields. The runtime deep-merges user YAML onto safe defaults from `opencontext_core.config.default_config_data()`.

| Field | Purpose | Default | Safe Value | Risky Value | Status | Related Command |
|---|---|---|---|---|---|---|
| `security` | Runtime posture, fail-closed behavior, default classification | private project | `mode: private_project`, `fail_closed: true` | external providers on without policy | Implemented | `opencontext doctor security` |
| `providers` | Global external provider switch | external off | `external_enabled: false` | `true` without provider policy | Implemented | `opencontext provider simulate` |
| `provider_policies` | Per-provider classification and retention rules | mock/local allow, external deny | require redaction/ZDR for external | training opt-in for private code | Implemented | `opencontext provider simulate` |
| `tools` | Native and MCP execution flags | disabled | `native.enabled: false`, `mcp.enabled: false` | write/network/MCP enabled broadly | Implemented boundary | `opencontext doctor tools` |
| `mcp` | MCP adapter policy under `tools.mcp` | disabled | disabled with allowlist required | stdio/network without sandbox | Scaffolded boundary | `opencontext doctor tools` |
| `traces` | Raw vs redacted context trace persistence | raw off, redacted on | `store_raw_context: false` | raw trace context | Implemented | `opencontext trace last` |
| `cache` | Exact and semantic cache policy | exact on, semantic off | exact local cache | semantic cache for confidential data | Interface implemented, semantic scaffolded | `opencontext cache plan` |
| `memory` | Progressive memory and harvesting policy | enabled, harvest off, approval on | `store_raw: false` | auto-harvest raw content | Implemented/scaffolded | `opencontext memory init` |
| `output` | Output mode and token cap | concise, 1500 | preserve warnings/paths/numbers | unlimited verbose output | Implemented | `opencontext ask --output-mode technical_terse` |
| `context` | Input budget, sections, ranking, compression | 12000 max input | reserve output and section budgets | no output reserve | Implemented | `opencontext pack` |
| `compression` | Global compression policy | adaptive protected spans | protected spans on | lossy code compression | Implemented/scaffolded | `opencontext doctor tokens` |
| `repo_map` | Repo map generation and symbol inclusion | enabled | include symbols, token cap | dumping raw files | Implemented | `opencontext inspect repomap` |
| `retrieval` | Retrieval and rerank sizes | hybrid top_k 20 | lower top_k for speed | excessive top_k | Implemented | `opencontext pack` |
| `workflows` | Named step sequences | code_assistant | local-safe steps | steps that bypass policy | Implemented/scaffolded | `opencontext workflows list` |
| `profiles` | Technology profile metadata | empty | first-party profile hints | framework code in core | Scaffolded | `opencontext init --template drupal` |
| `server` | API server defaults | disabled, 127.0.0.1:8000 | local bind | public bind without auth | Thin adapter | `uvicorn opencontext_api.main:app` |
| `egress` | Output/network/export policy | network deny | redacted clipboard/file export | webhook/network allow | Scaffolded | `opencontext prompt export` |
| `provider_cache` | Provider cache planning | explicit disabled | local planning only | provider cache without policy | Scaffolded | `opencontext cache plan` |
| `token_budgets` | Workflow input/output budgets | ask/plan/review/audit defaults | workflow-specific caps | no output cap | Scaffolded policy | `opencontext report cost` |
| `latency` | Workflow latency caps | ask 20s, plan 60s, audit 120s | local/cache-first | expensive model first | Scaffolded policy | `opencontext harness run` |
| `models` | Per-default/per-role/per-phase model routing (via MCP sampling hints) | client's default model | scope models per role/phase | external high-cost model as default | Implemented | `opencontext models show` / `opencontext profile` |
| `safety` | Secret scanning and prompt-injection detection | both on | `secret_scanning.redact: true` | scanning disabled | Implemented | `opencontext doctor security` |
| `knowledge_graph` | Code KG indexing and call analysis | enabled | scoped roots | dumping vendored/large trees | Implemented | `opencontext index .` |
| `sdd` | SDD orchestrator configuration | scaffolded | gated phases | bypassing gates | Implemented/scaffolded | `opencontext init` |
| `embedding` | Embedding provider/model for semantic retrieval | local/mock | local embeddings | external embeddings on private code | Implemented | `opencontext pack` |
| `harness` | Agentic harness governance (TDD / approval pre-gates) | scaffolded | approval-on for writes | writes without approval | Implemented/scaffolded | `opencontext harness run` |
| `auto_improve` | Opt-in self-tuning controls | off | leave off | unattended self-tuning | Scaffolded | `opencontext config show` |
| `skills` | Skill registry configuration | scaffolded | first-party skills | untrusted skills | Scaffolded | `opencontext config show` |
| `testing` | Testing configuration | scaffolded | local-safe | — | Scaffolded | `opencontext config show` |
| `context_planning` | Context planning configuration | scaffolded | defaults | — | Scaffolded | `opencontext pack` |
| `context_storage` | Context vector storage configuration | scaffolded | local storage | external storage of private code | Scaffolded | `opencontext config show` |
| `observability` | Observability/telemetry settings | local | local telemetry | external telemetry | Implemented/scaffolded | `opencontext telemetry show` |
| `context_packing` | Context pack assembly policy | defaults | section budgets | no budgets | Implemented | `opencontext pack` |
| `project_index` | Project indexing configuration | enabled | scoped roots | dumping large trees | Implemented | `opencontext index .` |
| `context_layers` | Named context-layer policies | empty | local-safe layers | layers that bypass policy | Scaffolded | `opencontext config show` |
| `commands` | Custom command definitions | empty | local-safe commands | shelling out broadly | Scaffolded | `opencontext config show` |
| `hooks` | Lifecycle hook commands | empty | local-safe hooks | untrusted hook commands | Scaffolded | `opencontext config show` |
| `ui_language` | UI language (`en` or `es`) | `en` | `en` / `es` | — | Implemented | `opencontext config show` |
| `project` | Project configuration | required | project metadata | — | Implemented | `opencontext config show` |

Example safe output policy:

```yaml
output:
  mode: concise
  max_output_tokens: 1500
  preserve: [code, commands, paths, symbols, warnings, numbers]
```

Example risky value to avoid:

```yaml
traces:
  store_raw_context: true
```

Raw trace context can contain private code or secrets and is disabled by default.
