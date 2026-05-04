"""Optional provider adapters kept outside OpenContext Core."""

from opencontext_providers.adapters import (
    ExternalProviderNotConfigured,
    MockProviderAdapter,
    OpenAICompatibleProviderAdapter,
    ProviderAdapter,
    ProviderAdapterConfig,
    ProviderAdapterRegistry,
    ProviderAdapterResult,
)

__all__ = [
    "ExternalProviderNotConfigured",
    "MockProviderAdapter",
    "OpenAICompatibleProviderAdapter",
    "ProviderAdapter",
    "ProviderAdapterConfig",
    "ProviderAdapterRegistry",
    "ProviderAdapterResult",
]
