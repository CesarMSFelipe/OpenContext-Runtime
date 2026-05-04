from __future__ import annotations

from pathlib import Path


def test_key_docs_exist_and_are_not_empty() -> None:
    docs = [
        Path("docs/configuration/reference.md"),
        Path("docs/security/ai-leak-and-prompt-security.md"),
        Path("docs/token-efficiency/output-token-control.md"),
        Path("docs/memory/overview.md"),
        Path("docs/enterprise/overview.md"),
    ]

    for path in docs:
        assert path.exists(), path
        assert len(path.read_text(encoding="utf-8").strip()) > 100
