"""Language detection and file classification helpers."""

from __future__ import annotations

from pathlib import Path

from opencontext_core.models.project import FileKind

LANGUAGE_BY_EXTENSION: dict[str, str] = {
    ".py": "python",
    ".php": "php",
    ".module": "php",
    ".install": "php",
    ".inc": "php",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".rst": "restructuredtext",
    ".twig": "twig",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
}

ASSET_EXTENSIONS: set[str] = {
    ".gif",
    ".ico",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".png",
    ".svg",
    ".webp",
}

CONFIG_FILENAMES: set[str] = {
    "pyproject.toml",
    "composer.json",
    "package.json",
    "tsconfig.json",
    "config/routes.yaml",
    "config/services.yaml",
}


def detect_language(path: Path) -> str:
    """Detect a language or file format from a file path."""

    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower(), "unknown")


def classify_file(path: Path) -> FileKind:
    """Classify a file into a coarse project-memory category."""

    rel = path.as_posix()
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in ASSET_EXTENSIONS:
        return FileKind.ASSET
    if "test" in path.parts or name.startswith("test_") or name.endswith("_test.py"):
        return FileKind.TEST
    if suffix in {".md", ".rst"} or rel.startswith("docs/"):
        return FileKind.DOCUMENTATION
    if suffix in {".twig", ".html", ".jinja", ".j2"} or "templates" in path.parts:
        return FileKind.TEMPLATE
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".xml"} or rel in CONFIG_FILENAMES:
        return FileKind.CONFIG
    if detect_language(path) in {"python", "php", "javascript", "typescript", "css", "scss", "sql"}:
        return FileKind.CODE
    return FileKind.UNKNOWN
