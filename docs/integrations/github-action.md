# Github Action

## Purpose
CI usage is scaffolded through safe configs and release/prompt/security audit commands.

## Current Status
CLI/API/local SDK paths are implemented. Agent-specific integrations are documented patterns unless a command explicitly exists.

## Setup
```bash
# Initialize checks + generate the GitHub Actions workflow
opencontext ci-check init
# Or generate the workflow only
opencontext ci-check github-actions   # [--force] overwrites existing
```
This creates `.github/workflows/opencontext-contextbench.yml`, which runs
`opencontext ci-check run --json` on every push/pull request and uploads the report as an artifact.

See [CI Checks](../guides/ci-checks.md) for defining check rules.
