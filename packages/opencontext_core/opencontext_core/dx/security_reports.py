"""Security scan/report helpers."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.config import DEFAULT_IGNORE_PATTERNS
from opencontext_core.indexing.scanner import ProjectScanner


class SecurityScanResult(BaseModel):
    """Redacted local security scan summary."""

    model_config = ConfigDict(extra="forbid")

    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def scan_project(root: str | Path = ".") -> SecurityScanResult:
    """Scan a project for secret-like content without returning raw values."""

    project_root = Path(root)
    if not project_root.exists():
        return SecurityScanResult(warnings=[f"Project root not found: {project_root}"])
    scanned = ProjectScanner(list(DEFAULT_IGNORE_PATTERNS)).scan(project_root)
    findings = []
    for item in scanned:
        if not item.metadata.get("contains_potential_secrets"):
            continue
        kinds = item.metadata.get("secret_finding_kinds", "unknown")
        findings.append(f"{item.relative_path}: {kinds}")
    warnings = ["Secret values are redacted from findings and reports."]
    if not findings:
        warnings.append(
            "No secret-like values found by the built-in scanner. "
            "Deep external scanners remain a future integration."
        )
    return SecurityScanResult(
        findings=findings,
        warnings=warnings,
    )
