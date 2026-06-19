"""Tests for plugin system."""

from __future__ import annotations

from pathlib import Path

import pytest

from opencontext_core.plugin_system import PluginRegistry


def _registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PluginRegistry:
    monkeypatch.setattr(
        PluginRegistry,
        "__init__",
        lambda self, plugins_dir=None: (
            setattr(self, "plugins_dir", tmp_path)
            or setattr(self, "_plugins", {})
            or setattr(self, "_commands", {})
            or setattr(self, "_hooks", {})
        ),
    )
    return PluginRegistry(tmp_path)


def _make_plugin(tmp_path: Path, name: str, *, checksum: str | None) -> None:
    import hashlib
    import json

    pdir = tmp_path / name
    pdir.mkdir()
    body = "class OpenContextPlugin:\n    name = 'p'\n"
    (pdir / "plugin.py").write_text(body, encoding="utf-8")
    info = {"name": name, "enabled": True, "entry_point": "plugin.py"}
    if checksum == "valid":
        info["entry_checksum"] = "sha256:" + hashlib.sha256(body.encode()).hexdigest()
    elif checksum == "tampered":
        info["entry_checksum"] = "sha256:" + ("0" * 64)
    (pdir / "plugin.json").write_text(json.dumps(info), encoding="utf-8")


def test_load_refuses_plugin_with_bad_checksum(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry(tmp_path, monkeypatch)
    _make_plugin(tmp_path, "evil", checksum="tampered")
    assert registry.load("evil") is None  # tampered entry point -> refused


def test_load_accepts_plugin_with_valid_checksum(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry(tmp_path, monkeypatch)
    _make_plugin(tmp_path, "good", checksum="valid")
    assert registry.load("good") is not None  # checksum matches -> loads


class TestPluginRegistry:
    """Test plugin registry."""

    def test_discover_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            PluginRegistry,
            "__init__",
            lambda self, plugins_dir=None: (
                setattr(self, "plugins_dir", tmp_path)
                or setattr(self, "_plugins", {})
                or setattr(self, "_commands", {})
                or setattr(self, "_hooks", {})
            ),
        )
        registry = PluginRegistry(tmp_path)
        plugins = registry.discover()
        assert plugins == []

    def test_enable_disable_nonexistent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            PluginRegistry,
            "__init__",
            lambda self, plugins_dir=None: (
                setattr(self, "plugins_dir", tmp_path)
                or setattr(self, "_plugins", {})
                or setattr(self, "_commands", {})
                or setattr(self, "_hooks", {})
            ),
        )
        registry = PluginRegistry(tmp_path)
        assert not registry.enable("nonexistent")
        assert not registry.disable("nonexistent")

    def test_register_command(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            PluginRegistry,
            "__init__",
            lambda self, plugins_dir=None: (
                setattr(self, "plugins_dir", tmp_path)
                or setattr(self, "_plugins", {})
                or setattr(self, "_commands", {})
                or setattr(self, "_hooks", {})
            ),
        )
        registry = PluginRegistry(tmp_path)
        registry.register_command("test", lambda: "result")
        assert "test" in registry.list_commands()
        assert registry.execute_command("test") == "result"

    def test_register_hook(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            PluginRegistry,
            "__init__",
            lambda self, plugins_dir=None: (
                setattr(self, "plugins_dir", tmp_path)
                or setattr(self, "_plugins", {})
                or setattr(self, "_commands", {})
                or setattr(self, "_hooks", {})
            ),
        )
        registry = PluginRegistry(tmp_path)
        registry.register_hook("event", lambda x: x * 2)
        results = registry.trigger_hook("event", 5)
        assert results == [10]
