"""Minimal no-op sample plugin for the plugin-compatibility golden gate.

Loads under the plugin sandbox import guard (no restricted imports) and exposes the
``OpenContextPlugin`` entry the loader looks for. Static-validation only — no live
provider, no Runtime mutation.
"""

from __future__ import annotations


class OpenContextPlugin:
    """A do-nothing plugin that satisfies the load + interface contract."""

    name = "sample-compat"
    version = "1.0.0"

    def activate(self) -> bool:
        """Activation hook — returns True to signal a clean, no-op activation."""
        return True

    def deactivate(self) -> None:
        """Deactivation hook — nothing to tear down."""
        return None
