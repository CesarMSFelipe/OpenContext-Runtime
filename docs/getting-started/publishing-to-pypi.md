# Publishing OpenContext to PyPI

Once the packages are published to PyPI, installation becomes simple:

```bash
pip install opencontext-core opencontext-cli
```

## Setup (One-time)

### 1. Create a PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account
3. Verify your email

### 2. Generate a PyPI API Token

1. Login to https://pypi.org
2. Go to Account Settings → **API tokens**
3. Click **"Add API token"**
4. Name it: `opencontext-publish`
5. Scope: **"Entire account"** (for all packages) or **"Project"** (per-package)
6. Copy the token (starts with `pypi-`)
   - ⚠️ You can only see it once - save it securely

### 3. Add GitHub Secret

1. Go to your repository: https://github.com/CesarMSFelipe/OpenContext-Runtime
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the token from step 2
6. Click **"Add secret"**

### 4. Verify the Workflow

Check `.github/workflows/publish.yml`:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: ${{ matrix.path }}/dist/
    print-hash: true
```

The workflow is already configured to:
- Build all 5 packages
- Publish to PyPI using the `PYPI_API_TOKEN` secret

## Publishing a Release

Once the setup is complete:

1. **Create a git tag** for the release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. **Create a GitHub release**:
   - Go to https://github.com/CesarMSFelipe/OpenContext-Runtime/releases
   - Click **"Create a new release"**
   - Tag: `v0.1.0`
   - Release title: `OpenContext Runtime v0.1.0`
   - Description: Release notes
   - Click **"Publish release"**

3. **GitHub Actions will automatically**:
   - Build all 5 packages
   - Run tests
   - Publish to PyPI

4. **Verify on PyPI**:
   - Visit https://pypi.org/project/opencontext-core/
   - Confirm all 5 packages are published

## Installation After Publishing

### Simple Installation
```bash
pip install opencontext-core opencontext-cli
```

### With Optional Features
```bash
# Full installation with API and profiles
pip install opencontext-core opencontext-cli opencontext-api opencontext-profiles

# With provider support
pip install opencontext-core[providers]
```

### Specific Version
```bash
pip install opencontext-core==0.1.0
```

## Package Dependencies

The dependency chain is:
- `opencontext-cli` → requires `opencontext-core` and `opencontext-profiles`
- `opencontext-api` → requires `opencontext-core` and `opencontext-profiles`
- `opencontext-providers` → requires `opencontext-core`
- `opencontext-profiles` → requires `opencontext-core`
- `opencontext-core` → requires `pydantic` and `PyYAML` only

**No circular dependencies.**

## What Gets Published

Each package publishes:
- Source distribution (`.tar.gz`)
- Built distribution/wheel (`.whl`)
- Metadata and README
- LICENSE file

## Troubleshooting

### "No distributions found"
- Ensure packages built successfully: `python -m build packages/opencontext_core`
- Check the workflow ran without errors in GitHub Actions

### "Invalid authentication credentials"
- Verify the token hasn't expired
- Regenerate if needed (old token will stop working)

### "Package already exists at this version"
- PyPI doesn't allow republishing the same version
- Increment version in `pyproject.toml` (e.g., `0.1.1`)
- Create a new tag and release

## After First Publish

Update README.md to show PyPI-first installation:

```bash
# Change from:
pip install -e packages/opencontext_core -e packages/opencontext_cli

# To:
pip install opencontext-core opencontext-cli
```

## Automatic Updates

The GitHub Actions workflow will automatically:
- Build on every release creation
- Skip if tests fail
- Publish to PyPI with version from `pyproject.toml`
- Create release artifacts with checksums
