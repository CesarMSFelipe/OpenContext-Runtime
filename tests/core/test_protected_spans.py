from __future__ import annotations

from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.compression import CompressionEngine
from opencontext_core.context.protection import ProtectedSpanManager
from opencontext_core.models.context import ContextItem, ContextPriority


def _engine() -> CompressionEngine:
    return CompressionEngine(
        OpenContextConfig.model_validate(default_config_data()).context.compression
    )


def _context(content: str) -> ContextItem:
    return ContextItem(
        id="protected",
        content=content,
        source="src/auth.py",
        source_type="file",
        priority=ContextPriority.P3,
        tokens=500,
        score=0.5,
    )


def test_code_block_preservation() -> None:
    content = "Keep this:\n```python\nSECRET = 123\n```\nExtra text " * 20
    result = _engine().compress_item(_context(content))

    assert result.item.content == content
    assert result.item.metadata["compression"]["reason"] == "protected_spans_detected"


def test_numeric_json_schema_and_file_path_are_protected() -> None:
    content = (
        '{"type": "object", "properties": {"count": {"type": "number"}}}\nsrc/Auth/User.php\n42'
    )
    spans = ProtectedSpanManager().detect(content)

    kinds = {span.kind for span in spans}
    assert {"json_schema", "file_path", "numeric_value"} <= kinds
    assert _engine().compress_item(_context(content)).item.content == content
