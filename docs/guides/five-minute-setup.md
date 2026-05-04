# Five-Minute Setup

OpenContext should be useful in less than five minutes on a normal local
project. The default path requires no API key, no external provider, no network
tools, no MCP, and no file-writing agent behavior.

## 1. Install

```bash
pipx install opencontext-runtime
```

For local repository development:

```bash
python3 -m pip install -e packages/opencontext_core -e packages/opencontext_profiles -e packages/opencontext_cli -e packages/opencontext_api
```

## 2. Initialize

```bash
cd my-project
opencontext init
opencontext onboard .
```

Use a profile template only when you already know the stack:

```bash
opencontext init --template python
opencontext init --template node
opencontext init --template drupal
```

Profiles add stack knowledge. They do not weaken core security defaults.

## 3. Index

```bash
opencontext index .
```

This writes a local project manifest under `.storage/opencontext/`. It does not
call an LLM.

## 4. Check Safety

```bash
opencontext doctor
opencontext doctor security
opencontext doctor tools
```

Expected defaults:

- external providers disabled,
- native tools disabled,
- MCP disabled,
- network denied,
- file writes denied,
- traces sanitized.

## 5. Generate Useful Context

```bash
opencontext pack . --query "Explain this project" --mode plan --copy
opencontext agent-context "Review access control" --target codex --copy
```

If clipboard support is unavailable, OpenContext prints the pack instead.

## Optional: Ask With Mock Mode

```bash
opencontext ask "Where is authentication implemented?"
```

The default mock provider is deterministic and local. Real provider adapters
must be enabled explicitly by policy.

## Optional: Stack-Specific Commands

```bash
opencontext validate --profile python
opencontext validate --profile node
opencontext validate --profile drupal
```

Validation commands are scaffolded in v0.1. Tests, linters, shell commands,
network tools, writes, and MCP remain blocked or approval-gated by policy.

## Mental Model

```text
OpenContext Core
  -> Technology Profiles
  -> Workflow Packs
  -> Adapters / Integrations
```

The core is universal and secure. Profiles provide optional stack intelligence.
Drupal is a first-party profile, not the product boundary.
