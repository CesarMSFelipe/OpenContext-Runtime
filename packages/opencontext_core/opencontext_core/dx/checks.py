"""Local check registry scaffolding."""

from __future__ import annotations

from pathlib import Path

CHECK_FILES: tuple[str, ...] = (
    "security-review.md",
    "context-leakage-review.md",
    "provider-policy-review.md",
    "profile-specific-review.md",
    "test-coverage-review.md",
)


def ensure_checks(root: Path) -> list[Path]:
    base = root / ".opencontext" / "checks"
    base.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name in CHECK_FILES:
        path = base / name
        path.touch(exist_ok=True)
        paths.append(path)
    return paths
