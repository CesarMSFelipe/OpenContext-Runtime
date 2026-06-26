"""Release ZIP hygiene tests."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


def test_gitattributes_excludes_local_state_and_envs() -> None:
    text = open(".gitattributes", encoding="utf-8").read()
    for path in (
        ".venv/",
        "venv/",
        ".ci-venv/",
        ".pytest_cache/",
        ".ruff_cache/",
        ".mypy_cache/",
        ".opencontext/",
        ".storage/",
        ".sdd/",
        ".tools/",
    ):
        assert f"{path} export-ignore" in text


def test_release_zip_builder_outputs_zip(tmp_path) -> None:
    sys.path.insert(0, str(Path.cwd()))
    from scripts.build_release_zip import build

    out = build(tmp_path / "release.zip")

    assert out.exists()
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert "pyproject.toml" in names
    assert not any(name.startswith((".git/", ".venv/", "venv/", ".storage/")) for name in names)
