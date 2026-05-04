"""Trace models for observability and auditability."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.compat import UTC
from opencontext_core.models.context import ContextItem, PromptSection, TokenBudget


class TraceEvent(BaseModel):
    """OpenTelemetry-compatible span event."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Event name.")
    timestamp: datetime = Field(description="Event timestamp.")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Event attributes.")


class TraceSpan(BaseModel):
    """OpenTelemetry-compatible span model without requiring an OTel dependency."""

    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(description="Trace identifier shared by related spans.")
    span_id: str = Field(description="Unique span identifier.")
    parent_span_id: str | None = Field(default=None, description="Parent span id.")
    name: str = Field(description="Span name.")
    start_time: datetime = Field(description="Span start timestamp.")
    end_time: datetime | None = Field(default=None, description="Span end timestamp.")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Span attributes.")
    events: list[TraceEvent] = Field(default_factory=list, description="Span events.")


class RuntimeTrace(BaseModel):
    """Complete trace for one runtime workflow execution."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(description="Unique run identifier.")
    trace_id: str = Field(
        default_factory=lambda: uuid4().hex,
        description="OpenTelemetry-compatible trace id.",
    )
    span_id: str = Field(
        default_factory=lambda: uuid4().hex[:16],
        description="Root span id.",
    )
    parent_span_id: str | None = Field(default=None, description="Root parent span id.")
    name: str = Field(default="workflow.run", description="Root span name.")
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Root span start time.",
    )
    end_time: datetime | None = Field(default=None, description="Root span end time.")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Root span attributes.")
    events: list[TraceEvent] = Field(default_factory=list, description="Root span events.")
    spans: list[TraceSpan] = Field(default_factory=list, description="Nested trace spans.")
    workflow_name: str = Field(description="Workflow that was executed.")
    input: str = Field(description="Original user request.")
    provider: str = Field(description="Selected LLM provider.")
    model: str = Field(description="Selected LLM model.")
    selected_context_items: list[ContextItem] = Field(
        description="Context items included in the prompt.",
    )
    discarded_context_items: list[ContextItem] = Field(
        description="Candidate context items excluded from the prompt.",
    )
    token_budget: TokenBudget = Field(description="Calculated token budget.")
    token_estimates: dict[str, int] = Field(description="Before and after token estimates.")
    compression_strategy: str = Field(description="Configured compression strategy.")
    prompt_sections: list[PromptSection] = Field(description="Assembled prompt sections.")
    final_answer: str = Field(description="Final LLM answer.")
    timings_ms: dict[str, float] = Field(
        default_factory=dict,
        description="Step durations in milliseconds.",
    )
    errors: list[str] = Field(default_factory=list, description="Errors captured during the run.")
    created_at: datetime = Field(description="UTC trace creation timestamp.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional trace metadata.",
    )
