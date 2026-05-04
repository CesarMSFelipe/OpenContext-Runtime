from __future__ import annotations

from pathlib import Path

import yaml

from opencontext_core.config import default_config_data


def write_config(tmp_path: Path, project_root: Path) -> Path:
    data = default_config_data()
    data["project"]["name"] = "test-project"
    data["project_index"]["root"] = str(project_root)
    data["retrieval"]["top_k"] = 10
    data["retrieval"]["rerank_top_k"] = 5
    config_path = tmp_path / "opencontext.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return config_path


def create_sample_project(root: Path) -> None:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "auth.py").write_text(
        "\n".join(
            [
                "class AuthService:",
                "    def login(self, username: str) -> bool:",
                "        return bool(username)",
                "",
                "def audit_login(username: str) -> str:",
                "    return username",
            ]
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Sample\nAuthentication lives in src/auth.py\n",
        encoding="utf-8",
    )
