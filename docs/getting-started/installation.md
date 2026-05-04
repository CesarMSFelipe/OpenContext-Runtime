# Installation

## Purpose
Install OpenContext Runtime for local, zero-key use or editable development.

## Current Status
The repository supports editable installs for `opencontext_core`, `opencontext_cli`, `opencontext_api`, and `opencontext_profiles`. Published package commands are documented as the intended distribution path.

## Commands
```bash
pipx install opencontext-runtime
python3 -m pip install -e packages/opencontext_core -e packages/opencontext_profiles -e packages/opencontext_cli -e packages/opencontext_api
opencontext --help
```

## Implemented Code
- CLI entry point: `packages/opencontext_cli/opencontext_cli/main.py`
- Core config loader: `packages/opencontext_core/opencontext_core/config.py`

## Planned Contents
Package publishing notes, signed release evidence, and platform-specific installation troubleshooting.
