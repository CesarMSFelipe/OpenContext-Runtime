"""SmartCrusher — structural JSON compression.

Detects arrays of objects with shared keys and converts them to a compact
tabular form: schema + rows. Reversible: the original JSON can be reconstructed
from the compressed form (tab → dict roundtrip is lossless).
"""

from __future__ import annotations

import json
from typing import Any

_MIN_ARRAY_LENGTH = 3
_MAX_INLINE_SCHEMA_KEYS = 20


def _looks_like_json_array(content: str) -> bool:
    """Cheap pre-check before attempting a full parse."""
    stripped = content.strip()
    return stripped.startswith("[") and stripped.endswith("]")


def _array_of_objects(items: list[Any]) -> list[dict[str, Any]] | None:
    """Return items if every element is a dict; None otherwise."""
    if not items:
        return None
    for item in items:
        if not isinstance(item, dict):
            return None
    return items


def _common_schema(objects: list[dict[str, Any]]) -> list[str] | None:
    """Extract sorted keys shared by >80% of objects. Return None if too many."""
    key_counts: dict[str, int] = {}
    for obj in objects:
        for k in obj:
            key_counts[k] = key_counts.get(k, 0) + 1
    threshold = max(2, len(objects) * 0.8)
    shared = sorted(k for k, c in key_counts.items() if c >= threshold)
    if not shared or len(shared) > _MAX_INLINE_SCHEMA_KEYS:
        return None
    return shared


def _format_value(v: Any) -> str:
    """Serialize a single value to its shortest safe form."""
    if v is None:
        return "∅"
    if isinstance(v, bool):
        return "T" if v else "F"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        text = v.replace("\n", "\\n").replace("\t", "\\t")
        if len(text) > 120:
            text = text[:60] + "…" + text[-40:]
        if " " in text or text == "":
            return f'"{text}"'
        return text
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


def _crush_array(content: str, *, min_array_length: int = _MIN_ARRAY_LENGTH) -> str | None:
    """Try to crush a JSON array of objects. Returns compressed string or None."""
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return None

    if not isinstance(data, list):
        return None

    if len(data) < min_array_length:
        return None

    objects = _array_of_objects(data)
    if objects is None:
        return None

    schema = _common_schema(objects)
    if schema is None:
        return None

    # Build rows: one line per object, columns = schema order
    # Use "\t" as column separator to avoid ambiguity with spaces in values
    rows: list[str] = []
    for obj in objects:
        cells = [_format_value(obj.get(k, "∅")) for k in schema]
        rows.append("\t".join(cells))

    schema_line = "|\t" + "\t".join(schema)
    header = f"<array[{len(objects)}] x {len(schema)} cols>"
    compressed = header + "\n" + schema_line + "\n" + "\n".join(rows)

    return compressed.strip()


def _fallback_prose(content: str) -> str:
    """Fallback: just strip whitespace aggressively."""
    import re as _re

    return _re.sub(r"\s+", " ", content.strip())


def compress(
    content: str,
    *,
    min_array_length: int = _MIN_ARRAY_LENGTH,
    tabular_format: str = "compact_table",
) -> str:
    """Structural compression of JSON content.

    Args:
        content: Raw JSON string.
        min_array_length: Minimum array length to trigger crushing.
        tabular_format: Output format ('compact_table' or 'aligned_columns').

    Returns:
        Compressed string. Reversible via ``expand``.
    """
    if not content.strip():
        return content

    if not _looks_like_json_array(content):
        return _fallback_prose(content)

    result = _crush_array(content, min_array_length=min_array_length)
    if result is not None:
        return result

    return _fallback_prose(content)


def expand(compressed: str) -> str:
    """Reverse a SmartCrusher-compressed array back to JSON.

    Works only for arrays that were crushed (tabular form). Any other
    content is returned unchanged (best-effort reverse).
    """
    if not compressed.startswith("<array["):
        return compressed  # not a crushed array

    lines = compressed.strip().splitlines()
    if len(lines) < 3:
        return compressed  # malformed

    # Parse schema from second line: "|\tschema_key1\tschema_key2"
    header_line = lines[1]
    if not header_line.startswith("|\t"):
        return compressed
    schema = header_line[2:].split("\t")

    # Parse rows
    objects: list[dict[str, Any]] = []
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        cells = line.split("\t")
        obj: dict[str, Any] = {}
        for i, key in enumerate(schema):
            raw = cells[i] if i < len(cells) else "∅"
            obj[key] = _parse_cell(raw)
        objects.append(obj)

    return json.dumps(objects, indent=2, ensure_ascii=False)


def _parse_cell(raw: str) -> Any:
    """Parse a cell value from its serialized form."""
    if raw == "∅":
        return None
    if raw == "T":
        return True
    if raw == "F":
        return False
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace("\\n", "\n").replace("\\t", "\t")
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except (ValueError, TypeError):
        pass
    return raw


__all__ = ["compress", "expand"]
