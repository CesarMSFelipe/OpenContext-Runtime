"""Incremental context garbage collection (PR-010, OC-CONTEXT-001 §Garbage Collection).

Compression is incremental: GC fires on four triggers — a second failed diagnosis,
a budget overflow, a workflow transition, and consolidation — and compacts the
ephemeral L1 layer, dropping obsolete/superseded reasoning while keeping the
load-bearing diagnostics/evidence/failed-strategies. It also emits the book output
format summarizing failed attempts, forbidden strategies, and the current verified
hypothesis. The output is redacted via :class:`SinkGuard` before return so no
chain-of-thought or secret can leak into durable context (design #7).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import StrEnum
from opencontext_core.safety.redaction import SinkGuard

# L1 keys whose content is load-bearing — never dropped by GC (book §Keep).
_KEEP_KEYS = frozenset(
    {
        "diagnostics",
        "evidence",
        "failed_strategies",
        "constraints",
        "acceptance_criteria",
        "signatures",
        "current_hypothesis",
    }
)

# L1 keys GC discards (book §Discard): obsolete/superseded/transient reasoning.
_DISCARD_KEYS = frozenset(
    {
        "obsolete_reasoning",
        "intermediate_reasoning",
        "superseded_attempts",
        "transient",
        "duplicated_tool_output",
        "scratch",
    }
)

# L1 keys GC compresses (book §Compress): repeated logs / long traces collapse to a
# deduplicated, head-limited form.
_COMPRESS_KEYS = frozenset({"logs", "repeated_logs", "stack_traces"})

_MAX_COMPRESSED_LINES = 5


class GcTrigger(StrEnum):
    """The four incremental-GC triggers (book §Garbage Collection)."""

    SECOND_FAILED_DIAGNOSIS = "second_failed_diagnosis"
    BUDGET_EXCEEDED = "budget_exceeded"
    WORKFLOW_TRANSITION = "workflow_transition"
    CONSOLIDATION = "consolidation"


class GcAttempt(BaseModel):
    """One failed attempt summarized for the GC output (book output format)."""

    model_config = ConfigDict(extra="forbid")

    attempt: int = Field(ge=1, description="1-based attempt number.")
    strategy: str = Field(default="", description="Strategy tried (becomes a 'do not retry').")
    reason: str = Field(default="", description="Why the attempt failed.")


def _compress_value(value: object) -> object:
    """Collapse a COMPRESS-classified value: dedupe + head-limit list/string lines."""
    if isinstance(value, list):
        seen: set[str] = set()
        out: list[object] = []
        for entry in value:
            key = str(entry)
            if key in seen:
                continue
            seen.add(key)
            out.append(entry)
            if len(out) >= _MAX_COMPRESSED_LINES:
                break
        dropped = len(value) - len(out)
        if dropped > 0:
            out.append(f"[... {dropped} repeated entries compressed ...]")
        return out
    if isinstance(value, str):
        lines: list[str] = []
        seen_lines: set[str] = set()
        for line in value.splitlines():
            if line in seen_lines:
                continue
            seen_lines.add(line)
            lines.append(line)
            if len(lines) >= _MAX_COMPRESSED_LINES:
                lines.append("[... repeated lines compressed ...]")
                break
        return "\n".join(lines)
    return value


def compact_l1(l1: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    """Compact an L1 dict: drop DISCARD keys, compress COMPRESS keys, keep the rest.

    Returns ``(compacted_l1, discarded_keys)``. KEEP keys and unknown keys are passed
    through verbatim (conservative: only explicitly-classified content is dropped).
    """
    compacted: dict[str, object] = {}
    discarded: list[str] = []
    for key, value in l1.items():
        if key in _DISCARD_KEYS:
            discarded.append(key)
            continue
        if key in _COMPRESS_KEYS:
            compacted[key] = _compress_value(value)
            continue
        compacted[key] = value
    return compacted, discarded


def _format_output(attempts: list[GcAttempt], hypothesis: str) -> str:
    """Build the book §GC output format (fact-only, redacted by the caller)."""
    lines: list[str] = []
    for att in attempts:
        reason = att.reason or "no diagnosis recorded"
        lines.append(f"Attempt {att.attempt} failed because {reason}.")
    forbidden = [att.strategy for att in attempts if att.strategy]
    for strategy in dict.fromkeys(forbidden):  # de-dupe, preserve order
        lines.append(f"Do not retry strategy {strategy}.")
    lines.append(f"Current verified hypothesis: {hypothesis or 'none yet'}.")
    return "\n".join(lines)


def collect(
    l1: dict[str, object],
    trigger: GcTrigger,
    attempts: list[GcAttempt] | None = None,
    *,
    hypothesis: str = "",
) -> tuple[dict[str, object], str]:
    """Run incremental GC over ``l1`` for ``trigger``; return (compacted_l1, output).

    ``output`` is the book attempt-summary, redacted via :class:`SinkGuard` so it is
    safe to persist into durable context. The compacted L1 records which trigger and
    which keys were dropped under ``_gc`` for the omission/budget receipts.
    """
    attempts = attempts or []
    compacted, discarded = compact_l1(l1)

    resolved_hypothesis = hypothesis or str(l1.get("current_hypothesis", "") or "")
    output = _format_output(attempts, resolved_hypothesis)
    redacted, _ = SinkGuard().redact(output)

    compacted["_gc"] = {
        "trigger": trigger.value,
        "discarded_keys": discarded,
        "attempts": len(attempts),
        "summary": redacted,
    }
    return compacted, redacted
