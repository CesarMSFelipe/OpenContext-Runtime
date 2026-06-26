"""ContextViewerScreen — shows the latest phase context JSON for the active run."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from opencontext_cli.tui.brand import BrandBar


class ContextViewerScreen(Screen[None]):
    """Shows the latest <phase>.context.json for the active oc-new run."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape,q", "dismiss", "Back"),
    ]

    DEFAULT_CSS = """
    ContextViewerScreen { background: #0B0F14; color: #E6EDF3; padding: 1 2; }
    #context-content { height: 1fr; overflow-y: auto; }
    """

    def compose(self) -> ComposeResult:
        yield BrandBar()
        yield Static(
            "[bold]Context pack[/]\n[dim]Latest phase context for active run[/]", markup=True
        )
        yield Static("", id="context-content", markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        content = self.query_one("#context-content", Static)
        content.update(self._render_context())

    def _render_context(self) -> str:
        try:
            from pathlib import Path

            from opencontext_core.oc_new.store import OcNewStore

            store = OcNewStore(".")
            state = store.latest()
            if state is None:
                return "[dim]No active run — no context to display.[/dim]"

            run_dir = Path(".opencontext") / "runs" / state.identity.run_id
            # Find the most recent <phase>.context.json file.
            context_files = sorted(run_dir.glob("*.context.json"), key=lambda p: p.stat().st_mtime)
            if not context_files:
                return f"[dim]No context files found for run {state.identity.run_id}.[/dim]"

            latest = context_files[-1]
            import json

            data = json.loads(latest.read_text())
            # Show first 2000 chars to avoid flooding the screen.
            text = json.dumps(data, indent=2)[:2000]
            return f"[bold]Context:[/] {latest.name}\n\n{text}"
        except Exception as exc:
            return f"[dim]Context unavailable: {exc}[/dim]"

    def action_dismiss(self, result: Any = None) -> None:  # type: ignore[override]
        self.app.pop_screen()
