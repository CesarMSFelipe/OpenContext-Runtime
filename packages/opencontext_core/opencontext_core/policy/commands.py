"""Deterministic command classification + forbidden-command enforcement.

``CommandClassifier.classify`` maps an arbitrary command string to exactly one of
six categories (SPEC CMD-2); classification is a deterministic rule table, never
model-driven (AD#4 / ``15-…#3.1``).

``CommandClassifier.is_forbidden`` promotes ``HarnessConfig.forbidden_commands``
— loaded from YAML but, until PR-005, read by **no execution path** — to real
enforcement (SPEC CMD-1, the documented bug-fix).
"""

from __future__ import annotations

from opencontext_core.compat import StrEnum


class CommandCategory(StrEnum):
    """The six command risk categories (SPEC CMD-2)."""

    SAFE = "safe"
    TEST = "test"
    PKG = "pkg"
    DESTRUCTIVE = "destructive"
    NETWORK = "network"
    UNKNOWN = "unknown"


# Ordered most-specific → least-specific. Destructive and network are checked
# before pkg/test/safe so e.g. ``curl ... | bash`` is NETWORK, ``rm -rf`` is
# DESTRUCTIVE, regardless of an incidental safe-looking token.
_DESTRUCTIVE = (
    "rm -rf",
    "rm -fr",
    "rm -r",
    "git push --force",
    "git push -f",
    "git reset --hard",
    "git clean -fd",
    "drop table",
    "drop database",
    "truncate table",
    "mkfs",
    "dd if=",
    "shutdown",
    "reboot",
    ":(){",
    "chmod -r 777",
    "> /dev/sda",
)

_NETWORK = (
    "curl ",
    "wget ",
    "ssh ",
    "scp ",
    "sftp ",
    "rsync ",
    "nc ",
    "ncat ",
    "netcat ",
    "telnet ",
    "ping ",
    "ftp ",
)

_PKG = (
    "pip install",
    "pip3 install",
    "uv pip install",
    "uv add",
    "pipx install",
    "poetry add",
    "poetry install",
    "npm install",
    "npm i ",
    "npm ci",
    "yarn add",
    "yarn install",
    "pnpm add",
    "pnpm install",
    "apt install",
    "apt-get install",
    "brew install",
    "cargo add",
    "go get",
    "gem install",
)

_TEST = (
    "pytest",
    "python -m pytest",
    "npm test",
    "npm run test",
    "yarn test",
    "go test",
    "cargo test",
    "tox",
    "jest",
    "vitest",
    "python -m unittest",
    "mvn test",
    "gradle test",
)

_SAFE = (
    "ls",
    "pwd",
    "cat ",
    "echo ",
    "grep ",
    "rg ",
    "find ",
    "head ",
    "tail ",
    "wc ",
    "git status",
    "git diff",
    "git log",
    "git show",
    "git branch",
    "ruff",
    "mypy",
    "black",
    "flake8",
    "isort",
)


class CommandClassifier:
    """Classify a command and enforce the configured deny-list."""

    def classify(self, command: str) -> CommandCategory:
        """Return the single risk category for *command* (SPEC CMD-2)."""
        normalized = " ".join(command.strip().lower().split())
        if not normalized:
            return CommandCategory.UNKNOWN
        # A piped fetch-and-execute is network egress even if it ends in ``bash``.
        if "| bash" in normalized or "| sh" in normalized or "|bash" in normalized:
            return CommandCategory.NETWORK
        if _matches(normalized, _DESTRUCTIVE):
            return CommandCategory.DESTRUCTIVE
        if _matches(normalized, _NETWORK):
            return CommandCategory.NETWORK
        if _matches(normalized, _PKG):
            return CommandCategory.PKG
        if _matches(normalized, _TEST):
            return CommandCategory.TEST
        if _starts(normalized, _SAFE):
            return CommandCategory.SAFE
        return CommandCategory.UNKNOWN

    def is_forbidden(self, command: str, denylist: list[str]) -> bool:
        """True when *command* matches a configured forbidden entry (SPEC CMD-1).

        Matching is normalized-substring: a denylist entry ``rm -rf`` blocks
        ``rm -rf build/`` and ``  RM   -RF  build`` alike. This is the wiring that
        makes ``forbidden_commands`` — previously inert — actually enforce.
        """
        normalized = " ".join(command.strip().lower().split())
        for raw in denylist:
            entry = " ".join(str(raw).strip().lower().split())
            if entry and entry in normalized:
                return True
        return False


def _matches(normalized: str, needles: tuple[str, ...]) -> bool:
    return any(needle in normalized for needle in needles)


def _starts(normalized: str, prefixes: tuple[str, ...]) -> bool:
    return any(normalized == prefix.strip() or normalized.startswith(prefix) for prefix in prefixes)
