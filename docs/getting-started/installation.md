# Installation

## Purpose
Install OpenContext Runtime for local development, testing, or production use.

## Current Status
All packages can be installed from source. PyPI publishing is configured but packages are not yet published.

## From Source (Development)
```bash
git clone https://github.com/CesarMSFelipe/OpenContext-Runtime.git
cd OpenContext-Runtime
python3 -m pip install -e packages/opencontext_core -e packages/opencontext_cli
# Optional: install API and profiles
python3 -m pip install -e packages/opencontext_api -e packages/opencontext_profiles
opencontext --help
```

## From PyPI (When Published)
```bash
python3 -m pip install opencontext-core opencontext-cli
# Optional: install API and profiles
python3 -m pip install opencontext-api opencontext-profiles
```

## Implemented Code
- CLI entry point: `packages/opencontext_cli/opencontext_cli/main.py`
- Core runtime: `packages/opencontext_core/opencontext_core/`
- API server: `packages/opencontext_api/opencontext_api/`
- Technology profiles: `packages/opencontext_profiles/opencontext_profiles/`

## Publishing
Packages are built and ready for PyPI publishing. The GitHub Actions workflow will publish on releases.
