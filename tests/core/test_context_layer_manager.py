from __future__ import annotations

from opencontext_core.operating_model import ContextLayerManager


def test_context_layer_manager_reads_config_layers() -> None:
    layers = ContextLayerManager().from_config(
        {"project": {"cacheable": True, "budget_tokens": 4000, "trust_level": "internal"}}
    )

    assert layers[0].name == "project"
    assert layers[0].cacheable is True
