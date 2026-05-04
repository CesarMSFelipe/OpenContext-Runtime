from __future__ import annotations

import json

from opencontext_core.memory_usability import ContextSerializer, SerializationFormat


def test_json_output_is_valid_and_redacted() -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    rendered = ContextSerializer().serialize({"token": secret}, SerializationFormat.JSON)

    assert json.loads(rendered)["token"] != secret


def test_toon_is_deterministic() -> None:
    data = {"b": 2, "a": [{"path": "src/auth.py"}]}
    serializer = ContextSerializer()

    assert serializer.serialize(data, "toon") == serializer.serialize(data, "toon")


def test_compact_list_smaller_than_verbose_markdown() -> None:
    rows = [{"path": "src/auth.py", "tokens": 10}, {"path": "src/api.py", "tokens": 8}]
    serializer = ContextSerializer()

    compact = serializer.serialize(rows, "compact_table")
    markdown = serializer.serialize(rows, "markdown")

    assert len(compact) < len(markdown)
