from pathlib import Path

from opencontext_core.workspace.layout import WORKSPACE_FILE_CONTENT, ensure_workspace

# Only files that carry real starter content are materialised eagerly.
REQUIRED_FILES = [
    "agents/README.md",
    "models/default.yaml",
    "policies/security-policy.yaml",
    "policies/permissions.yaml",
    "rules/security.md",
    "templates/untrusted_context.md",
    "playbooks/review-pr.yaml",
    "commands/review-pr.md",
]

# Empty placeholders that ``ensure_workspace`` must NOT create (artifact-footprint
# fix): they were 0-byte git litter and are made lazily on first real write.
SKIPPED_PLACEHOLDERS = [
    "project.md",
    "architecture.md",
    "decisions.md",
    "security.md",
    "workflows/code_review.yaml",
    "templates/system.md",
    "memory/repo_map.json",
    "memory/project-profile.md",
    "evals/security.yaml",
    "reports/security-scan.json",
]

# Working directories that must not be eagerly created as empty dirs.
SKIPPED_EMPTY_DIRS = [
    "cache",
    "context-packs",
    "plugins",
    "state",
    "traces",
    "runs",
    "approvals",
    "memory",
    "context-repository",
]


def test_workspace_templates_created(tmp_path: Path) -> None:
    ensure_workspace(tmp_path)
    base = tmp_path / ".opencontext"
    for rel in REQUIRED_FILES:
        path = base / rel
        assert path.exists(), rel
        assert path.read_text(encoding="utf-8").strip(), f"{rel} should have content"


def test_workspace_skips_empty_placeholders(tmp_path: Path) -> None:
    ensure_workspace(tmp_path)
    base = tmp_path / ".opencontext"
    for rel in SKIPPED_PLACEHOLDERS:
        assert not (base / rel).exists(), f"{rel} should not be materialised empty"
    for rel in SKIPPED_EMPTY_DIRS:
        assert not (base / rel).exists(), f"{rel} should not be eagerly created"


def test_only_content_files_are_materialised(tmp_path: Path) -> None:
    created = ensure_workspace(tmp_path)
    # Every created file maps to a non-empty content entry.
    assert created
    for path in created:
        assert path.is_file()
        assert path.stat().st_size > 0
    assert len(created) == len(WORKSPACE_FILE_CONTENT)
