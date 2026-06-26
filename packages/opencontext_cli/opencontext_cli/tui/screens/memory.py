"""MemoryBrowserScreen — lists available memory keys from the local backend."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static


class MemoryBrowserScreen(Screen[None]):
    """Lists memory keys from the local or Engram memory backend."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape,q", "dismiss", "Back"),
    ]

    DEFAULT_CSS = """
    MemoryBrowserScreen { background: #0B0F14; color: #E6EDF3; padding: 1 2; }
    #memory-content { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="memory-content", markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        content = self.query_one("#memory-content", Static)
        content.update(self._render_memory())

    def _render_memory(self) -> str:
        try:
            # NOTE: local_store is an optional backend; may not be present in all deployments.
            import importlib

            _ls = importlib.import_module("opencontext_core.memory.local_store")
            store = _ls.LocalMemoryStore(".")
            keys: list[str] = store.list_keys() if hasattr(store, "list_keys") else []
            if not keys:
                return "[dim]No memory keys found in local backend.[/dim]"
            lines = ["[bold]Memory keys:[/]"]
            for key in keys[:50]:
                lines.append(f"  • {key}")
            if len(keys) > 50:
                lines.append(f"  [dim]... and {len(keys) - 50} more[/dim]")
            return "\n".join(lines)
        except Exception:
            # NOTE: Fall back to engram bridge if local store is unavailable.
            try:
                import opencontext_core.memory.engram_bridge as _bridge

                # list_memory_keys is an optional helper; may not exist in all versions.
                list_keys = getattr(_bridge, "list_memory_keys", None)
                keys = list_keys() if callable(list_keys) else []
                if not keys:
                    return "[dim]No memory keys found.[/dim]"
                lines = ["[bold]Memory keys (Engram):[/]"]
                for key in keys[:50]:
                    lines.append(f"  • {key}")
                return "\n".join(lines)
            except Exception:
                return "[dim]Memory backend unavailable.[/dim]"

    def action_dismiss(self, result: Any = None) -> None:  # type: ignore[override]
        self.app.pop_screen()
