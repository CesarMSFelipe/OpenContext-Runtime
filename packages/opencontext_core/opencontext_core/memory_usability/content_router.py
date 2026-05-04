"""Route content to safe compression and serialization policies."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum
from opencontext_core.memory_usability.serializers import SerializationFormat


class ContentType(StrEnum):
    """Content categories understood by the memory/token usability layer."""

    CODE = "code"
    LOGS = "logs"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TRACE = "trace"
    TOOL_OUTPUT = "tool_output"
    MEMORY_FACT = "memory_fact"
    REPO_MAP = "repo_map"
    SECURITY_FINDING = "security_finding"
    WORKFLOW = "workflow"
    PLAIN_TEXT = "plain_text"
    UNKNOWN = "unknown"


class ContentRoute(BaseModel):
    """Routing decision for one content payload."""

    model_config = ConfigDict(extra="forbid")

    content_type: ContentType = Field(description="Detected content type.")
    compression_strategy: str = Field(description="Compression strategy key.")
    serialization_format: SerializationFormat = Field(description="Preferred serializer.")
    protected_spans: list[str] = Field(description="Protected span kinds.")
    security_policy: str = Field(description="Security policy name.")
    untrusted: bool = Field(default=True, description="Whether content must be wrapped as data.")


class ContentRouter:
    """Deterministically routes content by extension, structure, and source role."""

    def route(
        self,
        content: str,
        *,
        path: str | None = None,
        declared_type: ContentType | None = None,
    ) -> ContentRoute:
        """Return a safe route for content."""

        content_type = declared_type or self.detect(content, path=path)
        routes: dict[ContentType, tuple[str, SerializationFormat, list[str], str, bool]] = {
            ContentType.CODE: (
                "code_aware_symbol_selection",
                SerializationFormat.MARKDOWN,
                ["code", "paths", "symbols", "numbers"],
                "no_lossy_in_act_or_implement",
                True,
            ),
            ContentType.LOGS: (
                "head_tail_error_focused",
                SerializationFormat.COMPACT_TABLE,
                ["timestamps", "errors", "paths", "numbers"],
                "redact_tool_output",
                True,
            ),
            ContentType.JSON: (
                "structural_prune",
                SerializationFormat.JSON,
                ["keys", "numbers"],
                "redact_values",
                True,
            ),
            ContentType.YAML: (
                "structural_prune",
                SerializationFormat.TOON,
                ["keys", "numbers"],
                "redact_values",
                True,
            ),
            ContentType.TOOL_OUTPUT: (
                "tool_output_prune",
                SerializationFormat.MARKDOWN,
                ["errors", "commands", "paths"],
                "wrap_untrusted_redact",
                True,
            ),
            ContentType.REPO_MAP: (
                "repo_map_compact",
                SerializationFormat.TOON,
                ["paths", "symbols"],
                "no_raw_source",
                True,
            ),
            ContentType.SECURITY_FINDING: (
                "structured_finding",
                SerializationFormat.COMPACT_TABLE,
                ["fingerprints", "classifications"],
                "no_raw_secret",
                True,
            ),
        }
        default = routes.get(
            content_type,
            (
                "extractive_head_tail",
                SerializationFormat.MARKDOWN,
                ["paths", "numbers"],
                "redact",
                True,
            ),
        )
        return ContentRoute(
            content_type=content_type,
            compression_strategy=default[0],
            serialization_format=default[1],
            protected_spans=default[2],
            security_policy=default[3],
            untrusted=default[4],
        )

    def detect(self, content: str, *, path: str | None = None) -> ContentType:
        """Detect content type from path and basic structure."""

        suffix = Path(path or "").suffix.lower()
        if suffix in {".py", ".ts", ".js", ".php", ".go", ".rs", ".cs", ".java"}:
            return ContentType.CODE
        if suffix in {".json"}:
            return ContentType.JSON
        if suffix in {".yaml", ".yml"}:
            return ContentType.YAML
        if suffix in {".md", ".rst"}:
            return ContentType.MARKDOWN
        if suffix in {".log"}:
            return ContentType.LOGS
        if _looks_like_json(content):
            return ContentType.JSON
        if "trace_id" in content and "span_id" in content:
            return ContentType.TRACE
        if "SECURITY" in content or "secret" in content.lower():
            return ContentType.SECURITY_FINDING
        return ContentType.PLAIN_TEXT if content.strip() else ContentType.UNKNOWN


def _looks_like_json(content: str) -> bool:
    stripped = content.strip()
    if not stripped.startswith(("{", "[")):
        return False
    try:
        json.loads(stripped)
    except json.JSONDecodeError:
        return False
    return True
