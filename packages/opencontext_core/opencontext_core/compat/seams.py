"""The four named adapter seams (CL-001..004).

``HarnessApiAdapter`` is the canonical, shipped seam: it references the existing
``RuntimeApi`` HarnessRunner wrapper (runtime/api.py) -- it does NOT reimplement or
move it. ``adapt`` is the session-bracketed vNext route; ``legacy`` is the direct
HarnessRunner route. Both return the legacy ``RunResult`` unchanged, so they are
byte-equal on ``RunResult.legacy`` (the parity property other PRs assert).

The Workflow / Provider / Context seams are placeholders: they advertise their
subsystem, gating flag, and owning PR, and raise ``NotImplementedError`` until
PR-003 / PR-012 / PR-010 land their bodies. Importing them is inert.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class HarnessApiAdapter:
    """Canonical LegacyAdapter wrapping the shipped RuntimeApi run() seam (CL-001)."""

    subsystem = "runtime"
    flag = "runtime.session_wrapper"
    owning_pr = "PR-001"

    def __init__(
        self,
        root: Path | str = ".",
        *,
        config: Any = None,
        harness_factory: Any = None,
    ) -> None:
        self._root = root
        self._config = config
        self._harness_factory = harness_factory

    def _api(self, *, session_wrapper: bool) -> Any:
        # Imported lazily so `import opencontext_core.compat` never pulls in the
        # runtime package; the seam only touches it when actually invoked.
        from opencontext_core.runtime.api import RuntimeApi

        return RuntimeApi(
            self._root,
            config=self._config,
            session_wrapper=session_wrapper,
            harness_factory=self._harness_factory,
        )

    def adapt(self, request: Any) -> Any:
        """vNext route: bracket the legacy run with a RuntimeApi session."""
        return self._api(session_wrapper=True).run(request)

    def legacy(self, request: Any) -> Any:
        """Legacy route: call HarnessRunner.run() directly (no session writes)."""
        return self._api(session_wrapper=False).run(request)


class _DeferredSeam:
    """Base for a not-yet-implemented adapter seam; raises naming its owning PR."""

    subsystem: str = "?"
    flag: str = "?"
    owning_pr: str = "?"

    def _pending(self, route: str) -> NotImplementedError:
        return NotImplementedError(
            f"{type(self).__name__}.{route} lands in {self.owning_pr} "
            f"(subsystem={self.subsystem}, flag={self.flag})"
        )

    def adapt(self, *args: Any, **kwargs: Any) -> Any:
        raise self._pending("adapt")

    def legacy(self, *args: Any, **kwargs: Any) -> Any:
        raise self._pending("legacy")


class LegacyWorkflowAdapter(_DeferredSeam):
    """CL-002: WORKFLOW_TRACKS -> WorkflowDefinition (body lands in PR-003)."""

    subsystem = "workflow_registry"
    flag = "runtime.registry_enabled"
    owning_pr = "PR-003"


class LegacyProviderAdapter(_DeferredSeam):
    """CL-003: llm provider/sampling/firewall -> unified gateway (body in PR-012)."""

    subsystem = "provider_gateway"
    flag = "runtime.gateway_enabled"
    owning_pr = "PR-012"


class LegacyContextAdapter(_DeferredSeam):
    """CL-004: retrieval planner / packing -> ContextEnvelope (body in PR-010)."""

    subsystem = "context_engine"
    flag = "runtime.context_engine_enabled"
    owning_pr = "PR-010"
