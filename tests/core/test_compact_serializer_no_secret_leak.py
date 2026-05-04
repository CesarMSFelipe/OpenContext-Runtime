from __future__ import annotations

from opencontext_core.memory_usability import ContextSerializer


def test_compact_serializer_no_secret_leak() -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    rendered = ContextSerializer().serialize([{"secret": secret}], "compact_table")

    assert secret not in rendered
    assert "[REDACTED" in rendered
