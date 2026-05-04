from __future__ import annotations

from opencontext_cli.main import _template_config
from opencontext_core.config import OpenContextConfig


def test_core_templates_generate_valid_safe_config() -> None:
    templates = (
        "generic",
        "drupal",
        "symfony",
        "python",
        "node",
        "ci",
        "enterprise",
        "air-gapped",
    )
    for template in templates:
        config = OpenContextConfig.model_validate(_template_config(template))
        assert config.providers.external_enabled is False
        assert config.tools.mcp.enabled is False
        assert config.traces.store_raw_context is False
