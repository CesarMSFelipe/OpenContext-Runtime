from __future__ import annotations

from pathlib import Path

from opencontext_core.config import load_config


def test_prebuilt_configs_load_with_safe_defaults() -> None:
    for path in sorted(Path("configs").glob("opencontext*.yaml")):
        config = load_config(path)
        assert config.providers.external_enabled is False
        assert config.tools.mcp.enabled is False
        assert config.traces.store_raw_context is False
        assert config.cache.semantic.enabled is False
