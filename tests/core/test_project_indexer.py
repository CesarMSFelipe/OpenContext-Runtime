from __future__ import annotations

from pathlib import Path

from opencontext_core.config import ProjectIndexConfig
from opencontext_core.indexing.project_indexer import ProjectIndexer
from opencontext_profiles import first_party_profiles


def test_project_indexer_ignores_common_virtualenv_directory(tmp_path: Path) -> None:
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "installed.py").write_text(
        "class Dependency: ...\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("class App: ...\n", encoding="utf-8")
    config = ProjectIndexConfig(root=str(tmp_path), profile="generic")

    manifest = ProjectIndexer(config, "ignore-venv").build_manifest()

    assert [file.path for file in manifest.files] == ["src/app.py"]


def test_project_indexer_extracts_python_and_php_symbols(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text(
        "class UserService:\n    def authenticate(self):\n        return True\n",
        encoding="utf-8",
    )
    (tmp_path / "AuthController.php").write_text(
        "<?php\nclass AuthController {\n  public function login() {}\n}\n",
        encoding="utf-8",
    )
    config = ProjectIndexConfig(root=str(tmp_path), profile="generic", ignore=[])

    manifest = ProjectIndexer(config, "symbols").build_manifest()

    names = {symbol.name for symbol in manifest.symbols}
    assert {"UserService", "authenticate", "AuthController", "login"} <= names
    assert len(manifest.files) == 2


def test_drupal_profile_detection(tmp_path: Path) -> None:
    (tmp_path / "modules" / "custom").mkdir(parents=True)
    (tmp_path / "modules" / "custom" / "example.info.yml").write_text(
        "name: Example\n",
        encoding="utf-8",
    )
    (tmp_path / "example.module").write_text(
        "<?php\nfunction example_help() {}\n",
        encoding="utf-8",
    )
    config = ProjectIndexConfig(root=str(tmp_path), profile="generic", ignore=[])

    manifest = ProjectIndexer(config, "drupal", profiles=first_party_profiles()).build_manifest()

    assert "drupal" in manifest.technology_profiles
    assert manifest.profile == "drupal"


def test_symfony_profile_detection(tmp_path: Path) -> None:
    (tmp_path / "src" / "Controller").mkdir(parents=True)
    (tmp_path / "config").mkdir()
    (tmp_path / "src" / "Controller" / "HomeController.php").write_text(
        "<?php\nclass HomeController {}\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "routes.yaml").write_text("home: /home\n", encoding="utf-8")
    (tmp_path / "config" / "services.yaml").write_text("services: {}\n", encoding="utf-8")
    config = ProjectIndexConfig(root=str(tmp_path), profile="generic", ignore=[])

    manifest = ProjectIndexer(config, "symfony", profiles=first_party_profiles()).build_manifest()

    assert "symfony" in manifest.technology_profiles
    assert manifest.profile == "symfony"
