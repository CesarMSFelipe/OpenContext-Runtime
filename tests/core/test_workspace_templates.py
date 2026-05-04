from pathlib import Path

from opencontext_core.workspace.layout import ensure_workspace

REQUIRED_FILES = [
    "project.md",
    "architecture.md",
    "decisions.md",
    "security.md",
    "agents/README.md",
    "models/default.yaml",
    "policies/security-policy.yaml",
    "workflows/code_review.yaml",
    "rules/security.md",
    "templates/system.md",
    "memory/repo_map.json",
    "evals/security.yaml",
    "reports/security-scan.json",
]


def test_workspace_templates_created(tmp_path: Path) -> None:
    ensure_workspace(tmp_path)
    for rel in REQUIRED_FILES:
        assert (tmp_path / ".opencontext" / rel).exists(), rel
