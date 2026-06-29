"""Uniform YAML loader for built-in registry definitions (PR-006).

All three registries seed their built-ins from YAML under a ``builtins/`` directory,
mirroring the PR-003 ``workflows/builtins`` precedent. A file may hold either a
single definition (a mapping) or a list of definitions (a sequence of mappings), so
personas (one file) and skills (one file per category) share the same loader.

Layer L6: imports only pydantic + pyyaml + the local base.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


def load_defs_from_file[ModelT: BaseModel](
    path: str | Path, model_cls: type[ModelT]
) -> list[ModelT]:
    """Parse and validate every definition in a single YAML file.

    Accepts a top-level mapping (one definition) or a top-level list of mappings.
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [model_cls.model_validate(raw)]
    if isinstance(raw, list):
        return [model_cls.model_validate(item) for item in raw]
    raise ValueError(f"registry template {path} is neither a mapping nor a list")


def load_defs_from_dir[ModelT: BaseModel](
    directory: str | Path, model_cls: type[ModelT]
) -> list[ModelT]:
    """Load and validate every ``*.yaml`` definition under ``directory`` (sorted)."""
    root = Path(directory)
    if not root.is_dir():
        return []
    defs: list[ModelT] = []
    for path in sorted(root.glob("*.yaml")):
        defs.extend(load_defs_from_file(path, model_cls))
    return defs
