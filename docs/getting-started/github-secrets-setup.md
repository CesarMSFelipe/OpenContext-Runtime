# GitHub Secrets Setup for PyPI Publishing

This guide walks through creating the GitHub secret needed to automatically publish OpenContext packages to PyPI.

## Step 1: Create a PyPI Account & Token

### 1.1 Go to PyPI
- Visit https://pypi.org/account/register/
- Fill in username, email, password
- Verify your email

### 1.2 Generate API Token
1. Login to https://pypi.org
2. Click your username (top right) → Account Settings
3. Scroll down to **API tokens**
4. Click **"Add API token"**
5. **Token name**: `opencontext-github`
6. **Scope**: Select "Entire account" (to publish all packages)
7. Click **"Create token"**

### 1.3 Copy the Token
You'll see a long token like:
```
pypi-AgEIcHlwaS5vcmc...
```

⚠️ **IMPORTANT**: Copy this immediately - PyPI only shows it once!

---

## Step 2: Add to GitHub Secrets

### 2.1 Go to Repository Settings
1. Open https://github.com/CesarMSFelipe/OpenContext-Runtime
2. Click **Settings** (right side, top area)
3. Left sidebar → **Secrets and variables** → **Actions**

### 2.2 Create New Secret
1. Click **"New repository secret"** (green button, top right)
2. Fill in:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Paste your token from step 1.3
3. Click **"Add secret"**

You should now see `PYPI_API_TOKEN` in the Secrets list (✓ masked).

---

## Step 3: Verify the Workflow

The workflow at `.github/workflows/publish.yml` is already configured to use this secret:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: ${{ matrix.path }}/dist/
```

This uses the `PYPI_API_TOKEN` automatically via GitHub Actions environment.

---

## Step 4: Create Your First Release

When ready to publish:

```bash
# 1. Tag the release
git tag v0.1.0
git push origin v0.1.0

# 2. Create GitHub release
# Option A: Via CLI (if you have GitHub CLI installed)
gh release create v0.1.0 --generate-notes

# Option B: Via web UI
# - Go to https://github.com/CesarMSFelipe/OpenContext-Runtime/releases
# - Click "Create a new release"
# - Tag: v0.1.0
# - Title: "OpenContext Runtime v0.1.0"
# - Click "Publish release"
```

The workflow will automatically:
1. ✅ Build all 5 packages
2. ✅ Run tests
3. ✅ Publish to PyPI using the secret
4. ✅ Create release artifacts

---

## Step 5: Verify Publishing

Within 2-3 minutes, check:

- **PyPI packages**: https://pypi.org/project/opencontext-core/
- **GitHub release**: https://github.com/CesarMSFelipe/OpenContext-Runtime/releases/tag/v0.1.0
- **Workflow logs**: https://github.com/CesarMSFelipe/OpenContext-Runtime/actions

---

## Installation After Publishing

Once published:

```bash
# Simple one-liner
pip install opencontext-core opencontext-cli

# With all components
pip install opencontext-core opencontext-cli opencontext-api opencontext-profiles
```

---

## Troubleshooting

### Secret not working?
- **Check the name**: Must be exactly `PYPI_API_TOKEN`
- **Check the scope**: In `.github/workflows/publish.yml`, it uses this secret automatically
- **Regenerate token**: If old, create a new one on PyPI

### Publishing failed?
- Check **Actions** tab in GitHub for error logs
- Common issues:
  - Tests failed: Fix tests, re-tag, and retry
  - Version already published: Update version in `pyproject.toml`
  - Token expired: Regenerate on PyPI

### Token security
- ✅ GitHub masks secrets in logs automatically
- ✅ Never commit token to git
- ✅ Only visible to GitHub Actions (not in logs)
- ✅ Can rotate anytime by creating new token

---

## For Future Releases

Each new release just requires:

```bash
# 1. Update version in all pyproject.toml files
# 2. Commit changes
git add .
git commit -m "Bump version to 0.2.0"

# 3. Create tag
git tag v0.2.0
git push origin main
git push origin v0.2.0

# 4. Create release (triggers publishing automatically)
gh release create v0.2.0 --generate-notes
```

That's it! The secret stays in GitHub, and publishing is automatic.
