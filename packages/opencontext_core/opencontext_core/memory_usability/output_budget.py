"""Output token budgeting and terse-mode rendering."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum
from opencontext_core.context.budgeting import estimate_tokens


class OutputMode(StrEnum):
    """Supported output styles for user-facing runtime responses."""

    FULL = "full"
    CONCISE = "concise"
    TECHNICAL_TERSE = "technical_terse"
    STRUCTURED = "structured"
    PATCH_ONLY = "patch_only"
    REPORT = "report"
    JSON = "json"


class OutputBudgetResult(BaseModel):
    """Result of applying an output budget policy."""

    model_config = ConfigDict(extra="forbid")

    mode: OutputMode = Field(description="Resolved output mode.")
    content: str = Field(description="Budgeted output content.")
    original_tokens: int = Field(ge=0, description="Original output token estimate.")
    final_tokens: int = Field(ge=0, description="Final output token estimate.")
    max_output_tokens: int = Field(ge=0, description="Configured output budget.")
    truncated: bool = Field(description="Whether output was shortened.")
    preserved_markers: list[str] = Field(
        default_factory=list,
        description="Kinds of important content preserved during reduction.",
    )


class OutputBudgetController:
    """Controls output size while preserving technical facts and warnings."""

    def __init__(
        self,
        default_mode: OutputMode = OutputMode.CONCISE,
        max_output_tokens: int = 1500,
        preserve: list[str] | None = None,
    ) -> None:
        self.default_mode = default_mode
        self.max_output_tokens = max_output_tokens
        self.preserve = preserve or ["code", "commands", "paths", "symbols", "warnings", "numbers"]

    def apply(
        self,
        content: str,
        *,
        mode: OutputMode | str | None = None,
        max_output_tokens: int | None = None,
    ) -> OutputBudgetResult:
        """Apply an output mode and token cap to content."""

        resolved_mode = self.resolve_mode(mode)
        limit = max_output_tokens if max_output_tokens is not None else self.max_output_tokens
        original_tokens = estimate_tokens(content)
        rendered = self._render_mode(content, resolved_mode)
        final_tokens = estimate_tokens(rendered)
        truncated = False
        if limit > 0 and final_tokens > limit:
            rendered = _truncate_preserving_lines(rendered, limit)
            final_tokens = estimate_tokens(rendered)
            truncated = True
        return OutputBudgetResult(
            mode=resolved_mode,
            content=rendered,
            original_tokens=original_tokens,
            final_tokens=final_tokens,
            max_output_tokens=limit,
            truncated=truncated or rendered != content,
            preserved_markers=_preserved_markers(rendered),
        )

    def resolve_mode(self, mode: OutputMode | str | None) -> OutputMode:
        """Resolve user/config values to an OutputMode."""

        if mode is None:
            return self.default_mode
        if isinstance(mode, OutputMode):
            return mode
        return OutputMode(mode)

    def _render_mode(self, content: str, mode: OutputMode) -> str:
        if mode is OutputMode.FULL:
            return content
        if mode is OutputMode.PATCH_ONLY:
            patch_lines = [
                line
                for line in content.splitlines()
                if line.startswith(("diff ", "+++ ", "--- ", "@@ ", "+", "-"))
            ]
            return "\n".join(patch_lines) if patch_lines else "No patch content selected."
        if mode is OutputMode.TECHNICAL_TERSE:
            return _technical_terse(content)
        if mode in {OutputMode.STRUCTURED, OutputMode.JSON, OutputMode.REPORT}:
            return content.strip()
        return _concise(content)


def _concise(content: str) -> str:
    paragraphs = [line.strip() for line in content.splitlines() if line.strip()]
    return "\n".join(paragraphs[:20])


def _technical_terse(content: str) -> str:
    kept: list[str] = []
    in_code = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            kept.append(line)
            continue
        if in_code or _is_technical_line(stripped):
            kept.append(line)
        elif stripped and len(stripped.split()) <= 8:
            kept.append(stripped)
    return "\n".join(kept)


def _is_technical_line(line: str) -> bool:
    warning_terms = ("warning", "error", "blocked", "deny", "allow", "failed", "passed")
    return (
        any(term in line.lower() for term in warning_terms)
        or bool(re.search(r"[\w./-]+\.(py|md|yaml|yml|json|toml|php|ts|js)\b", line))
        or bool(re.search(r"\b[A-Za-z_][A-Za-z0-9_]{3,}\b", line))
        or bool(re.search(r"\b\d+(?:\.\d+)?\b", line))
        or line.startswith(("$ ", "opencontext ", "pytest", "ruff", "mypy"))
    )


def _truncate_preserving_lines(content: str, max_tokens: int) -> str:
    lines = content.splitlines()
    kept: list[str] = []
    for line in lines:
        candidate = "\n".join([*kept, line])
        if estimate_tokens(candidate) > max_tokens:
            break
        kept.append(line)
    if not kept and content:
        return content[: max(1, max_tokens * 4)]
    if len(kept) < len(lines):
        kept.append("[TRUNCATED: output budget reached]")
    return "\n".join(kept)


def _preserved_markers(content: str) -> list[str]:
    markers: list[str] = []
    checks = {
        "paths": r"[\w./-]+\.(py|md|yaml|yml|json|toml)",
        "numbers": r"\b\d+(?:\.\d+)?\b",
        "warnings": r"(?i)\b(warning|blocked|deny|error|failed)\b",
        "commands": r"(?m)^(opencontext|pytest|ruff|mypy|\$ )",
        "code": r"```|def |class ",
    }
    for name, pattern in checks.items():
        if re.search(pattern, content):
            markers.append(name)
    return markers
