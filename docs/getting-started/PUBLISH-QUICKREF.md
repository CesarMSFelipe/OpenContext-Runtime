# Quick Reference: Publish to PyPI

**One-time setup** (~5 minutes), then automated for every release.

## Setup Phase (One-time)

### 1. PyPI Account & Token
```bash
# Create account: https://pypi.org/account/register/
# Generate token: https://pypi.org → Account Settings → API tokens
# Copy token (starts with "pypi-")
```

### 2. GitHub Secret
```bash
# GitHub → Settings → Secrets and variables → Actions
# New secret: PYPI_API_TOKEN = <your_token>
```

### 3. Verify Workflow
- Check `.github/workflows/publish.yml` exists ✓

**Done!** Now every release publishes automatically.

---

## Release Phase (Repeatable)

### Make Release
```bash
# Update version in all pyproject.toml files (e.g., 0.1.0 → 0.2.0)
# Commit and push
git add .
git commit -m "Bump version to 0.2.0"
git push origin main
```

### Create Release
```bash
# Create git tag
git tag v0.2.0
git push origin v0.2.0

# Create GitHub release (triggers workflow automatically)
# Option A: CLI
gh release create v0.2.0 --generate-notes

# Option B: Web UI
# https://github.com/CesarMSFelipe/OpenContext-Runtime/releases/new
# - Tag: v0.2.0
# - Click "Publish release"
```

### Verify
```bash
# Check GitHub Actions: 
# https://github.com/CesarMSFelipe/OpenContext-Runtime/actions

# Check PyPI (after 2-3 minutes):
# https://pypi.org/project/opencontext-core/v0.2.0/
```

---

## Installation (After Publishing)

```bash
# Simple
pip install opencontext-core opencontext-cli

# With API
pip install opencontext-core opencontext-cli opencontext-api

# Specific version
pip install opencontext-core==0.2.0
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Secret not recognized | Verify name is exactly `PYPI_API_TOKEN` |
| Publishing failed | Check GitHub Actions logs for error |
| Version already exists | Increment version and re-tag |
| Can't login to PyPI | Generate new token, update GitHub secret |

---

## Files Modified

- `.github/workflows/publish.yml` - Builds and publishes packages
- `packages/*/pyproject.toml` - Version definitions
- `README.md` - Installation instructions
- `docs/getting-started/*.md` - Detailed guides

---

## Full Docs

- [Publishing to PyPI](publishing-to-pypi.md) - Complete reference
- [GitHub Secrets Setup](github-secrets-setup.md) - Detailed steps
