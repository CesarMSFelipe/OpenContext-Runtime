"""Provider adapter contracts and safe optional adapters."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class ExternalProviderNotConfigured(RuntimeError):
    """Raised when an optional external provider adapter has not been configured."""


class ProviderAdapterConfig(BaseModel):
    """Provider adapter configuration."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(description="Provider key.")
    model: str = Field(description="Model identifier.")
    endpoint: str | None = Field(default=None, description="Optional endpoint.")
    api_key_env: str | None = Field(default=None, description="Environment variable for API key.")
    enabled: bool = Field(default=False, description="External adapters are disabled by default.")


class ProviderAdapterResult(BaseModel):
    """Provider response returned through adapter packages."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(description="Provider response content.")
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    provider: str = Field(description="Provider key.")
    model: str = Field(description="Model id.")


class ProviderAdapter(Protocol):
    """Protocol implemented by optional provider adapters."""

    config: ProviderAdapterConfig

    def generate(self, prompt: str) -> ProviderAdapterResult:
        """Generate a response from a prompt."""


class MockProviderAdapter:
    """Deterministic local adapter for tests and zero-key mode."""

    def __init__(self, config: ProviderAdapterConfig | None = None) -> None:
        self.config = config or ProviderAdapterConfig(
            provider="mock",
            model="mock-llm",
            enabled=True,
        )

    def generate(self, prompt: str) -> ProviderAdapterResult:
        """Return a deterministic response without network access."""

        return ProviderAdapterResult(
            content=f"Mock provider response. Prompt chars={len(prompt)}.",
            input_tokens=max(1, len(prompt) // 4),
            output_tokens=8,
            provider=self.config.provider,
            model=self.config.model,
        )


class OpenAICompatibleProviderAdapter:
    """OpenAI-compatible adapter scaffold without importing provider SDKs."""

    def __init__(self, config: ProviderAdapterConfig) -> None:
        self.config = config

    def generate(self, prompt: str) -> ProviderAdapterResult:
        """Raise until an application supplies a real SDK-backed subclass."""

        _ = prompt
        raise ExternalProviderNotConfigured(
            "OpenAI-compatible adapter is a scaffold. Install/configure an application-level "
            "adapter outside opencontext_core and enable provider policy explicitly."
        )


class ProviderAdapterRegistry:
    """Small registry for optional provider adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, ProviderAdapter] = {}

    def register(self, adapter: ProviderAdapter) -> None:
        """Register a provider adapter."""

        self._adapters[adapter.config.provider] = adapter

    def get(self, provider: str) -> ProviderAdapter:
        """Return a registered adapter."""

        return self._adapters[provider]
