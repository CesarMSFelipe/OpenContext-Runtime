"""Tests for SmartCrusher — structural JSON compression."""

from __future__ import annotations

import json

from opencontext_core.compression.smart_crusher import compress, expand

_RECORDS = json.dumps([{"id": i, "name": f"item-{i}", "active": True} for i in range(5)])


def test_array_of_objects_produces_tabular_form() -> None:
    result = compress(_RECORDS)
    assert result.startswith("<array[5]")
    assert "id" in result
    assert "name" in result


def test_expand_roundtrip_restores_array() -> None:
    crushed = compress(_RECORDS)
    restored = expand(crushed)
    original = json.loads(_RECORDS)
    recovered = json.loads(restored)
    assert [r["id"] for r in recovered] == [r["id"] for r in original]


def test_non_json_falls_back_to_prose_strip() -> None:
    prose = "hello   world\n\nfoo  bar"
    result = compress(prose)
    assert result == "hello world foo bar"


def test_short_array_skips_crushing() -> None:
    short = json.dumps([{"x": 1}, {"x": 2}])
    result = compress(short, min_array_length=3)
    # Falls back — no tabular header
    assert not result.startswith("<array[")


def test_expand_passthrough_for_non_crushed() -> None:
    plain = "just some text"
    assert expand(plain) == plain
