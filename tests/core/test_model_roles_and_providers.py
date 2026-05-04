from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.providers import provider_repo_map, provider_security_report
from opencontext_core.models.context import DataClassification
from opencontext_core.plugins.manifest import PluginManifest


def test_default_model_roles_present() -> None:
    config = OpenContextConfig.model_validate(default_config_data())
    assert "generate" in config.models.roles
    assert config.models.roles["generate"].provider == "mock"


def test_context_provider_items_are_internal_and_typed() -> None:
    item = provider_repo_map("repo summary")
    assert item.classification is DataClassification.INTERNAL
    assert item.source == "@repo_map"
    security = provider_security_report("secure")
    assert security.source == "@security_report"


def test_plugin_manifest_extended_fields() -> None:
    plugin = PluginManifest(name="demo", version="1.0.0", entrypoint="plugins.demo:main")
    assert plugin.type == "analyzer"
    assert plugin.max_data_classification is DataClassification.INTERNAL
