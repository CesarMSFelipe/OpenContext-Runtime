"""Built-in skill definition templates shipped with OpenContext (PR-006)."""

from __future__ import annotations

from pathlib import Path


def builtins_dir() -> Path:
    """Return the directory holding the built-in skill definition YAML files."""
    return Path(__file__).resolve().parent
