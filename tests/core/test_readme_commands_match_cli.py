from __future__ import annotations

from opencontext_cli.main import _build_parser


def test_readme_critical_commands_exist_in_cli_help() -> None:
    help_text = _build_parser().format_help()

    for command in ("onboard", "index", "pack", "memory", "release", "prompt", "cache"):
        assert command in help_text
