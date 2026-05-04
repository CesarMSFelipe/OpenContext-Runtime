"""Token reporting helpers for frictionless diagnostics."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.config import DEFAULT_IGNORE_PATTERNS
from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.indexing.scanner import ProjectScanner, is_ignored


class TokenReport(BaseModel):
    """Token-efficiency report for a workspace or persisted manifest."""

    model_config = ConfigDict(extra="forbid")

    baseline_indexable_files: int = Field(default=0, ge=0)
    baseline_raw_character_count: int = Field(default=0, ge=0)
    total_indexable_tokens: int = Field(default=0, ge=0)
    top_token_files: list[str] = Field(default_factory=list)
    ignored_token_files: list[str] = Field(default_factory=list)
    ignored_paths: list[str] = Field(default_factory=list)
    included_context_tokens: int = Field(default=0, ge=0)
    omitted_context_tokens: int = Field(default=0, ge=0)
    compression_savings: int = Field(default=0, ge=0)
    cache_savings: int = Field(default=0, ge=0)
    prompt_cache_eligible_tokens: int = Field(default=0, ge=0)


def build_token_report(root: str | Path | None = None, *, limit: int = 10) -> TokenReport:
    """Build a deterministic token report.

    Calling without a root preserves the v0.1 scaffold shape used by tests and
    external consumers. Passing a root performs a local-only scan that respects
    `.gitignore`, `.opencontextignore`, and built-in noise filters.
    """

    if root is None:
        return TokenReport()
    resolved_root = Path(root).resolve()
    if not resolved_root.exists():
        return TokenReport()
    scanned = ProjectScanner(list(DEFAULT_IGNORE_PATTERNS)).scan(resolved_root)
    top_entries = sorted(scanned, key=lambda item: (-item.tokens, item.relative_path))[:limit]
    total = sum(item.tokens for item in scanned)
    ignored_entries = _ignored_token_entries(resolved_root)[:limit]
    return TokenReport(
        baseline_indexable_files=len(scanned),
        baseline_raw_character_count=sum(len(item.content) for item in scanned),
        total_indexable_tokens=total,
        top_token_files=[f"{item.relative_path}: {item.tokens}" for item in top_entries],
        ignored_token_files=[f"{path}: {tokens}" for path, tokens in ignored_entries],
        ignored_paths=[path for path, _ in ignored_entries],
        included_context_tokens=total,
        prompt_cache_eligible_tokens=sum(
            item.tokens for item in scanned if item.file_type.value != "asset"
        ),
    )


def suggest_opencontextignore(root: str | Path | None = None) -> list[str]:
    """Suggest ignore patterns that usually reduce token pressure safely."""

    suggestions = ["**/dist/**", "package-lock.json"]
    if root is None:
        return suggestions
    report = build_token_report(root)
    for entry in report.top_token_files:
        path = entry.split(": ", 1)[0]
        if _looks_like_generated_or_bulk(path):
            suggestions.append(path)
    return sorted(dict.fromkeys(suggestions))


def _ignored_token_entries(root: Path) -> list[tuple[str, int]]:
    patterns = _effective_ignore_patterns(root)
    entries: list[tuple[str, int]] = []
    for current_root, directory_names, file_names in os.walk(root):
        current_path = Path(current_root)
        directory_names[:] = [
            name for name in directory_names if name not in {".git", "__pycache__"}
        ]
        for file_name in file_names:
            path = current_path / file_name
            if not is_ignored(path, root, patterns) or not path.is_file():
                continue
            content = _read_text(path)
            tokens = estimate_tokens(content) if content else max(1, path.stat().st_size // 4)
            entries.append((path.relative_to(root).as_posix(), tokens))
    return sorted(entries, key=lambda item: (-item[1], item[0]))


def _effective_ignore_patterns(root: Path) -> list[str]:
    patterns = list(DEFAULT_IGNORE_PATTERNS)
    for ignore_file in (root / ".gitignore", root / ".opencontextignore"):
        if not ignore_file.exists() or not ignore_file.is_file():
            continue
        for line in ignore_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            normalized = line.strip()
            if normalized and not normalized.startswith("#"):
                patterns.append(normalized)
    return list(dict.fromkeys(patterns))


def _read_text(path: Path) -> str:
    raw = path.read_bytes()[:1_000_000]
    if b"\x00" in raw[:2048]:
        return ""
    return raw.decode("utf-8", errors="ignore")


def _looks_like_generated_or_bulk(path: str) -> bool:
    markers = (
        "/dist/",
        "/build/",
        "/coverage/",
        "package-lock.json",
        "composer.lock",
        ".min.js",
        ".min.css",
    )
    normalized = f"/{path}"
    return any(marker in normalized for marker in markers)
