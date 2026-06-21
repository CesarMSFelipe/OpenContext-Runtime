# OpenCode & Kilo Code

## Purpose
OpenCode and Kilo Code share a compatible config format. OpenContext
generates MCP config, SDD orchestrator profile, and AGENTS.md instructions.

## Setup

```bash
opencontext onboard
opencontext setup opencode      # or: opencontext setup opencode --scope global
opencontext setup kilo-code
```

For OpenCode (`--scope global`) this creates:
- `~/.config/opencode/mcp.json` — MCP server config
- `~/.config/opencode/agents/sdd-orchestrator.json` — SDD orchestrator profile (plus oc-*.md agent profiles)
- `AGENTS.md` (project root) — Instructions

For Kilo Code (`--scope global`):
- `~/.config/kilo/mcp.json` — MCP server config
- `AGENTS.md` (project root) — Instructions

With the default `--scope local`, mcp.json/agents are written under the project instead of `~/.config`; AGENTS.md is always project-root.

## Available Commands

```bash
# Code exploration
opencontext pack . --query "Review auth" --mode plan --copy
opencontext index .
opencontext inspect repomap

# SDD workflow
opencontext init        # Initialize SDD context
# Then in the agent: /oc-new <change>

# Health & updates
opencontext verify
opencontext update
opencontext upgrade

# Plugin management
opencontext plugin search
opencontext plugin install <name>
opencontext plugin update
opencontext plugin info <name>
opencontext plugin list --json

# Configuration
opencontext config show
opencontext config reconfigure plugins
opencontext config backup
opencontext config restore <id>
```

## SDD Orchestrator Profile

The installed `sdd-orchestrator` agent profile gives OpenCode access to
the full SDD lifecycle via the knowledge graph MCP tools.

## MCP Tools (all 14)

| Tool | Purpose |
|------|---------|
| `opencontext_search` | Find symbols by name across the codebase |
| `opencontext_context` | Build relevant code context for a task |
| `opencontext_callers` / `opencontext_callees` | Trace call flow |
| `opencontext_impact` | Analyze what code is affected by changing a symbol |
| `opencontext_node` | Get details about a specific symbol |
| `opencontext_files` | Get indexed file structure |
| `opencontext_status` | Check index health and statistics |
| `opencontext_trace` | Find the shortest path between two symbols in the call graph |
| `opencontext_replace_symbol_body` | Replace a named symbol's definition span with new source |
| `opencontext_insert_before_symbol` | Insert source immediately before a named symbol |
| `opencontext_insert_after_symbol` | Insert source immediately after a named symbol |
| `opencontext_rename_symbol` | Rename a symbol at its definition and call-graph references |
| `opencontext_run` | Drive the SDD agentic loop in-process using the host's selected model |

## Related Commands

```bash
opencontext setup opencode
opencontext setup kilo-code
opencontext agent-context "Explain auth flow" --target opencode --copy
```
