from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from opencontext_core.config import default_config_data, load_config
from opencontext_core.errors import ConfigurationError


def test_config_loading_merges_required_ignore_patterns(tmp_path: Path) -> None:
    data = default_config_data()
    data["project_index"]["ignore"] = ["custom-cache"]
    config_path = tmp_path / "opencontext.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    config = load_config(config_path)

    assert config.project.name == "example-project"
    assert "custom-cache" in config.project_index.ignore
    assert "dist" in config.project_index.ignore
    assert config.models.default.provider == "mock"


def test_missing_config_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        load_config(tmp_path / "missing.yaml")
