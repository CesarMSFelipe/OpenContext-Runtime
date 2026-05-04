"""ContextEngine lifecycle hook interfaces."""

from __future__ import annotations

from collections.abc import Callable

from opencontext_core.models.workflow import WorkflowRunState

Hook = Callable[[WorkflowRunState], None]


class ContextEngineHooks:
    """Lifecycle hooks for pre/post workflow execution."""

    def __init__(self, before_run: Hook | None = None, after_run: Hook | None = None) -> None:
        self.before_run = before_run
        self.after_run = after_run
