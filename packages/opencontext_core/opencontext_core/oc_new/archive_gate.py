"""Archive gate — enforces that all phase evidence is present before archiving."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar


class OcNewArchiveGate:
    REQUIRED: ClassVar[list[str]] = [
        "explore.artifact.json",
        "propose.artifact.json",
        "spec.artifact.json",
        "design.artifact.json",
        "tasks.artifact.json",
        "approval.json",
        "apply-manifest.json",
        "verify-report.json",
        "review-report.json",
        "compliance-matrix.json",
        "harness-report.json",
    ]

    def validate(self, run_dir: Path) -> list[str]:
        return [name for name in self.REQUIRED if not (run_dir / name).exists()]

    def assert_can_archive(self, run_dir: Path) -> None:
        missing = self.validate(run_dir)
        if missing:
            raise RuntimeError("Cannot archive; missing: " + ", ".join(missing))
