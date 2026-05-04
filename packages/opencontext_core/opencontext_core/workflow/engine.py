"""Configurable workflow engine."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from time import perf_counter
from uuid import uuid4

from opencontext_core.compat import UTC
from opencontext_core.config import OpenContextConfig
from opencontext_core.errors import ConfigurationError
from opencontext_core.models.workflow import WorkflowRunState, WorkflowStepResult
from opencontext_core.workflow.hooks import ContextEngineHooks
from opencontext_core.workflow.steps import (
    WorkflowServices,
    context_apply,
    context_archive,
    context_compress,
    context_explore,
    context_pack,
    context_propose,
    context_rank,
    context_review,
    context_test,
    context_up_code,
    context_verify,
    embeddings_generate,
    llm_generate,
    project_load_manifest,
    project_retrieve,
    prompt_assemble,
    trace_persist,
    trace_sdd_persist,
)

WorkflowStep = Callable[[WorkflowRunState, WorkflowServices], str]


class WorkflowEngine:
    """Executes named YAML workflows through an explicit step registry."""

    def __init__(
        self,
        config: OpenContextConfig,
        services: WorkflowServices,
        registry: dict[str, WorkflowStep] | None = None,
        hooks: ContextEngineHooks | None = None,
    ) -> None:
        self.config = config
        self.services = services
        self.registry = registry or default_step_registry()
        self.hooks = hooks or ContextEngineHooks()

    def run(self, workflow_name: str, user_request: str) -> WorkflowRunState:
        """Execute a named workflow."""

        workflow = self.config.workflows.get(workflow_name)
        if workflow is None:
            raise ConfigurationError(f"Unknown workflow: {workflow_name}")
        state = WorkflowRunState(
            run_id=str(uuid4()),
            workflow_name=workflow_name,
            user_request=user_request,
        )
        if self.hooks.before_run is not None:
            self.hooks.before_run(state)
        for step_name in workflow.steps:
            step = self.registry.get(step_name)
            if step is None:
                raise ConfigurationError(f"Unknown workflow step: {step_name}")
            step_start = datetime.now(tz=UTC)
            started = perf_counter()
            summary = step(state, self.services)
            duration_ms = (perf_counter() - started) * 1000
            step_end = datetime.now(tz=UTC)
            state.step_results.append(
                WorkflowStepResult(
                    name=step_name,
                    duration_ms=duration_ms,
                    summary=summary,
                    start_time=step_start,
                    end_time=step_end,
                )
            )
        if self.hooks.after_run is not None:
            self.hooks.after_run(state)
        return state


def default_step_registry() -> dict[str, WorkflowStep]:
    """Return the built-in workflow step registry."""

    return {
        # Core workflow steps
        "project.load_manifest": project_load_manifest,
        "project.retrieve": project_retrieve,
        "context.rank": context_rank,
        "context.pack": context_pack,
        "context.compress": context_compress,
        "prompt.assemble": prompt_assemble,
        "llm.generate": llm_generate,
        "trace.persist": trace_persist,
        # SDD-style workflow steps
        "context.explore": context_explore,
        "context.propose": context_propose,
        "context.apply": context_apply,
        "context.test": context_test,
        "context.verify": context_verify,
        "context.review": context_review,
        "context.archive": context_archive,
        "context.up-code": context_up_code,
        "trace.sdd_persist": trace_sdd_persist,
        # Embedding generation
        "embeddings.generate": embeddings_generate,
    }
