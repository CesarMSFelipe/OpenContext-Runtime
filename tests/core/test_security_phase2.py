from __future__ import annotations

from pathlib import Path

from opencontext_core.cache.base import build_cache_key, cache_allowed_for_classifications
from opencontext_core.config import DEFAULT_IGNORE_PATTERNS
from opencontext_core.indexing.scanner import ProjectScanner
from opencontext_core.safety.pii import BasicPiiScanner


def test_scanner_respects_gitignore_and_opencontextignore(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (root / ".opencontextignore").write_text("skip.me\n", encoding="utf-8")
    (root / "ignored.txt").write_text("a", encoding="utf-8")
    (root / "skip.me").write_text("b", encoding="utf-8")
    (root / "ok.py").write_text("print('ok')", encoding="utf-8")

    scanner = ProjectScanner(list(DEFAULT_IGNORE_PATTERNS))
    scanned = scanner.scan(root)
    paths = {item.relative_path for item in scanned}

    assert "ok.py" in paths
    assert "ignored.txt" not in paths
    assert "skip.me" not in paths


def test_basic_pii_scanner_detects_email_and_phone() -> None:
    findings = BasicPiiScanner().scan("email a@b.com phone +1 555 444 3333")
    kinds = {item.kind for item in findings}
    assert "email" in kinds
    assert "phone" in kinds


def test_cache_key_includes_security_scopes() -> None:
    key = build_cache_key(
        workflow_name="code_assistant",
        tenant_id="t1",
        project_id="p1",
        project_hash="abc",
        provider="mock",
        model_name="mock-llm",
        prompt_version="v1",
        user_input="hello",
        context="ctx",
        classifications=("internal", "confidential"),
    )
    assert key.tenant_id == "t1"
    assert key.project_id == "p1"
    assert key.provider == "mock"


def test_cache_disallowed_for_secret_or_regulated() -> None:
    assert cache_allowed_for_classifications(("internal",)) is True
    assert cache_allowed_for_classifications(("secret",)) is False
    assert cache_allowed_for_classifications(("regulated", "internal")) is False
