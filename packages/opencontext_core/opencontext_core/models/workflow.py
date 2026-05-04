"""Workflow state and result models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.context import (
    AssembledPrompt,
    ContextItem,
    ContextPackResult,
    TokenBudget,
)
from opencontext_core.models.llm import LLMResponse
from opencontext_core.models.project import ProjectManifest
from opencontext_core.models.trace import RuntimeTrace


class WorkflowInput(BaseModel):
    """User input and workflow selection for a runtime run."""

    model_config = ConfigDict(extra="forbid")

    user_request: str = Field(description="User request to answer.")
    workflow_name: str = Field(default="code_assistant", description="Configured workflow name.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional caller metadata.",
    )


class WorkflowStepResult(BaseModel):
    """Execution summary for a workflow step."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Step name.")
    duration_ms: float = Field(ge=0.0, description="Step duration in milliseconds.")
    summary: str = Field(description="Short step summary for traces and diagnostics.")
    start_time: datetime = Field(description="Step start timestamp.")
    end_time: datetime = Field(description="Step end timestamp.")


class WorkflowRunState(BaseModel):
    """Mutable workflow state passed between registered steps."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    run_id: str = Field(description="Unique run identifier.")
    workflow_name: str = Field(description="Workflow being executed.")
    user_request: str = Field(description="Original user request.")
    manifest: ProjectManifest | None = Field(default=None, description="Loaded manifest.")
    retrieved_context: list[ContextItem] = Field(
        default_factory=list,
        description="Retrieved context candidates.",
    )
    ranked_context: list[ContextItem] = Field(
        default_factory=list,
        description="Ranked context candidates.",
    )
    selected_context: list[ContextItem] = Field(
        default_factory=list,
        description="Context selected for prompt assembly.",
    )
    discarded_context: list[ContextItem] = Field(
        default_factory=list,
        description="Context excluded by ranking or budget decisions.",
    )
    context_pack: ContextPackResult | None = Field(
        default=None,
        description="Context packing result.",
    )
    token_budget: TokenBudget | None = Field(default=None, description="Calculated token budget.")
    prompt: AssembledPrompt | None = Field(default=None, description="Assembled prompt.")
    llm_response: LLMResponse | None = Field(default=None, description="LLM response.")
    trace: RuntimeTrace | None = Field(default=None, description="Persisted trace.")
    step_results: list[WorkflowStepResult] = Field(
        default_factory=list,
        description="Executed workflow step summaries.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Implementation details shared between steps.",
    )
