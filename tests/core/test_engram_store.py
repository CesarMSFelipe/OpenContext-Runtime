"""Tests for EngramMemoryAdapter — 3 cases."""

from __future__ import annotations

import pytest

from opencontext_core.exceptions import BackendUnavailableError
from opencontext_core.memory.agent import AgentMemoryStore
from opencontext_core.memory.engram_store import EngramMemoryAdapter


def test_unavailable_endpoint_raises_backend_unavailable_error() -> None:
    with pytest.raises(BackendUnavailableError):
        EngramMemoryAdapter(endpoint="http://localhost:19999")


def test_error_message_contains_persistent_memory_not_external_name() -> None:
    with pytest.raises(BackendUnavailableError) as exc_info:
        EngramMemoryAdapter(endpoint="http://localhost:19999")
    msg = str(exc_info.value).lower()
    assert "persistent-memory" in msg
    # Must NOT mention "engram" or any external service name
    assert "engram" not in msg


def test_satisfies_agent_memory_store_protocol() -> None:
    """EngramMemoryAdapter's class signature satisfies Protocol (structural check)."""
    # We cannot instantiate without a server, so check structurally.
    adapter_cls = EngramMemoryAdapter
    required_methods = {"search", "write", "reinforce", "contradict", "decay", "failure_boost"}
    actual_methods = {name for name in dir(adapter_cls) if not name.startswith("_")}
    assert required_methods.issubset(actual_methods)
