from __future__ import annotations

from pathlib import Path

from opencontext_providers import (
    ExternalProviderNotConfigured,
    MockProviderAdapter,
    OpenAICompatibleProviderAdapter,
    ProviderAdapterConfig,
)


def test_mock_provider_adapter_runs_without_api_keys() -> None:
    result = MockProviderAdapter().generate("hello")

    assert result.provider == "mock"
    assert result.model == "mock-llm"
    assert "Prompt chars=5" in result.content


def test_external_provider_adapter_is_scaffolded_and_disabled_by_default() -> None:
    adapter = OpenAICompatibleProviderAdapter(
        ProviderAdapterConfig(provider="openai-compatible", model="example")
    )

    try:
        adapter.generate("hello")
    except ExternalProviderNotConfigured as exc:
        assert "scaffold" in str(exc)
    else:
        raise AssertionError("External provider adapter should not call a provider by default")


def test_opencontext_core_does_not_import_provider_package() -> None:
    core_root = Path("packages/opencontext_core/opencontext_core")
    matches = [
        path
        for path in core_root.rglob("*.py")
        if "opencontext_providers" in path.read_text(encoding="utf-8")
    ]

    assert matches == []
