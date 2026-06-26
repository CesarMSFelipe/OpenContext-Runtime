"""BudgetScreen — shows budget ledger for the active oc-new run."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from opencontext_cli.tui.brand import BrandBar


class BudgetScreen(Screen[None]):
    """Shows token budget usage for the active oc-new run."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape,q", "dismiss", "Back"),
    ]

    DEFAULT_CSS = """
    BudgetScreen { background: #0B0F14; color: #E6EDF3; padding: 1 2; }
    #budget-content { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield BrandBar()
        yield Static("[bold]Budget[/]\n[dim]Token ledger for active run[/]", markup=True)
        yield Static("", id="budget-content", markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        content = self.query_one("#budget-content", Static)
        content.update(self._render_budget())

    def _render_budget(self) -> str:
        try:
            from opencontext_core.agentic.budget import BudgetLedger
            from opencontext_core.oc_new.store import OcNewStore

            store = OcNewStore(".")
            state = store.latest()
            if state is None:
                return "[dim]No active run — budget data unavailable.[/dim]"

            from pathlib import Path

            ledger_path = (
                Path(".opencontext") / "runs" / state.identity.run_id / "budget_ledger.json"
            )
            if not ledger_path.exists():
                return "No active run"

            ledger = BudgetLedger.model_validate_json(ledger_path.read_text())
            lines = [
                f"[bold]Run:[/] {state.identity.run_id}",
                f"[bold]Used total:[/] {ledger.used_total} tokens",
                "",
                "[bold]Phases:[/]",
            ]
            for p in ledger.phases:
                lines.append(
                    f"  {p.phase:<12} in={p.used_input_tokens:>6}  out={p.used_output_tokens:>6}"
                )
            total_budget = ledger.total_budget
            if total_budget:
                remaining = total_budget - ledger.used_total
                lines.append(
                    f"\n[bold]Budget:[/] {ledger.used_total} / {total_budget}"
                    f"  ({remaining} remaining)"
                )
            return "\n".join(lines)
        except Exception:
            return "No active run"

    def action_dismiss(self, result: Any = None) -> None:  # type: ignore[override]
        self.app.pop_screen()
