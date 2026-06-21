# Windsurf

## Purpose
Windsurf reads project rules from `.windsurf/rules/`. OpenContext generates
a rules file with plan/code mode instructions.

## Setup

```bash
opencontext install
opencontext agent init --target windsurf
```

This creates project-local `.windsurf/rules/opencontext.md`.

Run `opencontext setup windsurf` to write Windsurf's MCP config (`mcpServers`).

## Available Commands

```bash
# Code exploration
opencontext pack . --query "Review auth" --mode plan --copy
opencontext index .
opencontext knowledge-graph view --format tree

# Health
opencontext verify
opencontext update
opencontext upgrade

# Plugins
opencontext plugin search
opencontext plugin install <name>
opencontext plugin info <name>

# Config
opencontext config show
opencontext config reconfigure plugins
```

## Related Commands

```bash
opencontext agent init --target windsurf
opencontext agent-context "Review access control" --target windsurf --copy
```
