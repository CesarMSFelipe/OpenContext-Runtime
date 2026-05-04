"""Compression quality gates for memory and context compaction."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.context.budgeting import estimate_tokens


class CompressionQualityReport(BaseModel):
    """Quality and safety report for one compression operation."""

    model_config = ConfigDict(extra="forbid")

    original_tokens: int = Field(ge=0, description="Original token estimate.")
    compressed_tokens: int = Field(ge=0, description="Compressed token estimate.")
    savings_percent: float = Field(ge=0.0, description="Estimated savings percentage.")
    protected_spans_preserved: bool = Field(description="Whether protected spans survived.")
    symbols_preserved: bool = Field(description="Whether symbol-like identifiers survived.")
    numbers_preserved: bool = Field(description="Whether numeric values survived.")
    source_refs_preserved: bool = Field(description="Whether source refs survived.")
    quality_risk: str = Field(description="Low/medium/high risk label.")
    reversible: bool = Field(description="Whether exact reconstruction is available.")
    expansion_available: bool = Field(description="Whether source expansion is available.")


class CompressionQualityGate:
    """Validates that compression preserved important facts."""

    def evaluate(
        self,
        original: str,
        compressed: str,
        *,
        protected_spans: list[str] | None = None,
        reversible: bool = False,
        expansion_available: bool = False,
    ) -> CompressionQualityReport:
        """Return a deterministic quality report."""

        original_tokens = estimate_tokens(original)
        compressed_tokens = estimate_tokens(compressed)
        protected = protected_spans or []
        protected_preserved = all(span in compressed for span in protected)
        symbols_preserved = _symbols(original).issubset(_symbols(compressed))
        numbers_preserved = _numbers(original).issubset(_numbers(compressed))
        source_refs_preserved = _source_refs(original).issubset(_source_refs(compressed))
        high_risk = not all(
            [protected_preserved, symbols_preserved, numbers_preserved, source_refs_preserved]
        )
        savings = (
            max(0.0, (original_tokens - compressed_tokens) / original_tokens * 100)
            if original_tokens
            else 0.0
        )
        return CompressionQualityReport(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            savings_percent=savings,
            protected_spans_preserved=protected_preserved,
            symbols_preserved=symbols_preserved,
            numbers_preserved=numbers_preserved,
            source_refs_preserved=source_refs_preserved,
            quality_risk="high" if high_risk else "low",
            reversible=reversible,
            expansion_available=expansion_available,
        )


def _symbols(text: str) -> set[str]:
    return set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{3,}\b", text))


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def _source_refs(text: str) -> set[str]:
    return set(re.findall(r"[\w./-]+\.(?:py|md|yaml|yml|json|toml)(?::\d+)?", text))
