"""Deterministic compact serializers for context and memory data."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

import yaml  # type: ignore[import-untyped]

from opencontext_core.compat import StrEnum
from opencontext_core.safety.redaction import SinkGuard


class SerializationFormat(StrEnum):
    """Supported structured output formats."""

    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    TOON = "toon"
    COMPACT_TABLE = "compact_table"


class ContextSerializer:
    """Serializes context metadata without leaking secrets."""

    def serialize(self, data: Any, fmt: SerializationFormat | str) -> str:
        """Serialize data in a deterministic, redacted format."""

        resolved = SerializationFormat(fmt)
        safe_data = _redact_data(data)
        if resolved is SerializationFormat.JSON:
            return json.dumps(safe_data, indent=2, sort_keys=True)
        if resolved is SerializationFormat.YAML:
            return str(yaml.safe_dump(safe_data, sort_keys=True))
        if resolved is SerializationFormat.TOON:
            return _to_toon(safe_data)
        if resolved is SerializationFormat.COMPACT_TABLE:
            return _to_compact_table(safe_data)
        return _to_markdown(safe_data)


def _redact_data(data: Any) -> Any:
    guard = SinkGuard()
    if hasattr(data, "model_dump"):
        data = data.model_dump(mode="json")
    if isinstance(data, Mapping):
        return {str(key): _redact_data(value) for key, value in sorted(data.items())}
    if isinstance(data, list | tuple):
        return [_redact_data(value) for value in data]
    if isinstance(data, str):
        return guard.redact(data)[0]
    return data


def _to_markdown(data: Any) -> str:
    if isinstance(data, list):
        return "\n".join(f"- {_inline(value)}" for value in data)
    if isinstance(data, Mapping):
        return "\n".join(f"- {key}: {_inline(value)}" for key, value in data.items())
    return str(data)


def _to_toon(data: Any) -> str:
    lines: list[str] = []
    _append_toon(lines, data, level=0, key=None)
    return "\n".join(lines)


def _append_toon(lines: list[str], value: Any, *, level: int, key: str | None) -> None:
    prefix = "  " * level
    label = f"{key}: " if key is not None else ""
    if isinstance(value, Mapping):
        lines.append(f"{prefix}{label}{{")
        for child_key, child_value in value.items():
            _append_toon(lines, child_value, level=level + 1, key=str(child_key))
        lines.append(f"{prefix}}}")
    elif isinstance(value, Sequence) and not isinstance(value, str):
        lines.append(f"{prefix}{label}[{len(value)}]")
        for item in value:
            _append_toon(lines, item, level=level + 1, key="-")
    else:
        lines.append(f"{prefix}{label}{value}")


def _to_compact_table(data: Any) -> str:
    rows = data if isinstance(data, list) else [data]
    if not rows:
        return ""
    normalized = [_row_dict(row) for row in rows]
    headers = sorted({key for row in normalized for key in row})
    lines = ["|".join(headers)]
    for row in normalized:
        lines.append("|".join(str(row.get(header, "")) for header in headers))
    return "\n".join(lines)


def _row_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return {str(key): _inline(value) for key, value in row.items()}
    return {"value": _inline(row)}


def _inline(value: Any) -> str:
    if isinstance(value, Mapping):
        return "{" + ", ".join(f"{key}={_inline(child)}" for key, child in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_inline(item) for item in value) + "]"
    return str(value)
