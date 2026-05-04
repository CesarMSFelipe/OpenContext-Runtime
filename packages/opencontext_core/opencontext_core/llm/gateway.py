"""Provider-neutral LLM gateway interface."""

from __future__ import annotations

from typing import Protocol

from opencontext_core.models.llm import LLMRequest, LLMResponse


class LLMGateway(Protocol):
    """Interface implemented by hosted and local LLM providers."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for a provider-neutral request."""
