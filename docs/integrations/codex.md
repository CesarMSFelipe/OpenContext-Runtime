# Codex CLI

## Purpose
Codex CLI uses `AGENTS.md` for project instructions. OpenContext generates
this file with MCP tool documentation and all CLI commands.

## Setup

```bash
opencontext onboard
opencontext setup codex      # wire MCP into ~/.codex/config.toml
opencontext agent init --target codex
```

This creates `AGENTS.md` in the project root with the full OpenContext reference.

## Available Commands

```bash
# Code exploration
opencontext pack . --query "Review auth" --mode plan --copy
opencontext index .
opencontext inspect repomap

# Health
opencontext verify
opencontext verify --json

# Updates
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
opencontext agent init --target codex
opencontext agent-context "Review access control" --target codex --copy
```
