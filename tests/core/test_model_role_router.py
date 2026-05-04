from __future__ import annotations

from opencontext_core.operating_model import ModelRoleRouter


def test_model_role_router_defaults_to_mock() -> None:
    assert ModelRoleRouter().route("critic") == {"provider": "mock", "model": "mock-llm"}
