"""Guard: every interactive prompt must route through ``opencontext_core.prompts``.

Two crashes and one hang shipped because TTY-only code used ``Prompt.ask`` /
``Confirm.ask`` / ``input()`` directly and the test suite never exercised those
paths. This scans the live source for those raw calls so a regression fails in
CI instead of in a user's terminal. The single allowed home for the raw calls is
``prompts.py`` itself (the wrapper). Numeric value entry via ``IntPrompt.ask`` is
allowed — it is a value, not a menu.
"""

from __future__ import annotations

import re
from pathlib import Path

# Word-boundaried so IntPrompt.ask / RichConfirm.ask don't match; input() only
# when it's a bare builtin call, not a ``something.input(`` method.
_PATTERNS = [
    re.compile(r"\bPrompt\.ask\b"),
    re.compile(r"\bConfirm\.ask\b"),
    # The dx BrandConsole has no .ask(); calling it crashes at runtime. Interactive
    # input must go through prompts.* — not the console. (runtime.ask / IntPrompt.ask
    # are fine: an LLM query and a numeric value, neither a user menu.)
    re.compile(r"\bconsole\.ask\s*\("),
    re.compile(r"(?<![\w.])input\s*\("),
]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCE_ROOTS = [
    _REPO_ROOT / "packages" / "opencontext_cli" / "opencontext_cli",
    _REPO_ROOT / "packages" / "opencontext_core" / "opencontext_core",
]
# The one module allowed to call the raw prompts — it IS the wrapper.
_ALLOWED = {"prompts.py"}


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for root in _SOURCE_ROOTS:
        for path in root.rglob("*.py"):
            if "build" in path.parts or path.name in _ALLOWED:
                continue
            files.append(path)
    return files


def test_no_raw_interactive_prompts_in_live_source() -> None:
    offenders: list[str] = []
    for path in _iter_source_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(p.search(line) for p in _PATTERNS):
                rel = path.relative_to(_REPO_ROOT)
                offenders.append(f"{rel}:{lineno}: {line.strip()}")

    assert not offenders, (
        "Raw interactive prompt(s) found — route them through "
        "`opencontext_core.prompts` (select/checkbox/confirm/text/secret):\n" + "\n".join(offenders)
    )


def test_guard_actually_sees_the_source() -> None:
    # Sanity: the scanner must be pointed at real files, or the guard is a no-op.
    files = _iter_source_files()
    assert len(files) > 50
    assert any(f.name == "menu_cmd.py" for f in files)
