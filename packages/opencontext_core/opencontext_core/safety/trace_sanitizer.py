"""Sanitize traces before persistence."""

from __future__ import annotations

from typing import Any

from opencontext_core.config import SecurityMode
from opencontext_core.models.trace import RuntimeTrace
from opencontext_core.safety.redaction import SinkGuard


class TraceSanitizer:
    def sanitize(self, trace: RuntimeTrace, mode: SecurityMode) -> RuntimeTrace:
        if mode is SecurityMode.DEVELOPER:
            return trace
        redacted_sections = [
            section.model_copy(update={"content": "[REDACTED]", "redacted": True})
            for section in trace.prompt_sections
        ]
        redacted_selected = [
            item.model_copy(update={"content": "[REDACTED]"})
            for item in trace.selected_context_items
        ]
        redacted_discarded = [
            item.model_copy(update={"content": "[REDACTED]"})
            for item in trace.discarded_context_items
        ]
        return trace.model_copy(
            update={
                "input": "[REDACTED]",
                "final_answer": "[REDACTED]",
                "prompt_sections": redacted_sections,
                "selected_context_items": redacted_selected,
                "discarded_context_items": redacted_discarded,
                "metadata": _sanitize_metadata(trace.metadata),
            }
        )


def _sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            if key == "content":
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = _sanitize_metadata(child)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    if isinstance(value, str):
        return SinkGuard().redact(value)[0]
    return value
