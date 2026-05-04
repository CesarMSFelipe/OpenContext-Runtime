from __future__ import annotations

from pathlib import Path

from opencontext_core.config import ProjectIndexConfig
from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.indexing.project_indexer import ProjectIndexer
from opencontext_core.indexing.repo_map import RepoMapEngine


def test_repo_map_generation_symbol_inclusion_and_budget(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "auth.py").write_text(
        "class AuthService:\n    def login(self):\n        return True\n",
        encoding="utf-8",
    )
    manifest = ProjectIndexer(
        ProjectIndexConfig(root=str(tmp_path), profile="generic", ignore=[]),
        "repo-map",
    ).build_manifest()

    engine = RepoMapEngine()
    repo_map = engine.build(manifest)
    rendered = engine.render(repo_map, max_tokens=80)

    assert repo_map.entries
    assert "src/auth.py" in rendered
    assert "AuthService" in rendered
    assert estimate_tokens(rendered) <= 80
    assert repo_map.token_estimate >= repo_map.entries[0].token_estimate


def test_repo_map_query_relevant_ordering(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "auth.py").write_text(
        "class AuthService:\n    def login(self):\n        return True\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "billing.py").write_text("class Invoice:\n    pass\n", encoding="utf-8")
    manifest = ProjectIndexer(
        ProjectIndexConfig(root=str(tmp_path), profile="generic", ignore=[]),
        "repo-map",
    ).build_manifest()

    repo_map = RepoMapEngine().build(manifest, query="authentication login")

    assert repo_map.entries[0].file_path == "src/auth.py"
