# Contributing

- Run `ruff check .`, `ruff format --check .`, `mypy packages/opencontext_core`, and `pytest` before PRs.
- Keep core package framework-agnostic and provider-agnostic.
- Add tests for all security-sensitive changes.

## Dev setup

- Local install: `make dev` (editable install of core/cli/api plus dev tools).
- Before opening a PR, run `make ci` to reproduce the GitHub `test` pipeline
  exactly: pinned ruff/mypy/pytest (via `requirements-ci.txt`) plus a build of
  all 5 packages in a fresh venv. If `make ci` is green, CI is green.

The per-tool commands above remain the quick path.
