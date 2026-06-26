"""GraphCanvas — Textual widget for interactive ASCII graph rendering.

Key bindings: arrow keys / hjkl for pan, +/- for zoom, 1-5 for mode filter.
Non-TTY guard: when sys.stdout.isatty() returns False, ``render()`` returns a
plain text adjacency-list fallback and no Textual widget is instantiated.
"""

from __future__ import annotations

import sys
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget

from opencontext_cli.tui.graph.models import GraphEdgeView, GraphMode, GraphNodeView, GraphViewState
from opencontext_cli.tui.graph.renderer import AsciiGraphRenderer
from opencontext_cli.tui.graph.viewport import GraphViewport


class GraphCanvas(Widget):
    """Interactive ASCII graph canvas with pan, zoom, and mode-filter bindings."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("up,k", "pan_up", "Pan up"),
        Binding("down,j", "pan_down", "Pan down"),
        Binding("left,h", "pan_left", "Pan left"),
        Binding("right,l", "pan_right", "Pan right"),
        Binding("+,equal", "zoom_in", "Zoom in"),
        Binding("-,minus", "zoom_out", "Zoom out"),
        Binding("1", "mode_run", "RUN mode"),
        Binding("2", "mode_kg", "KG mode"),
        Binding("3", "mode_memory", "MEMORY mode"),
        Binding("4", "mode_context", "CONTEXT mode"),
        Binding("5", "mode_impact", "IMPACT mode"),
    ]

    def __init__(
        self,
        nodes: list[GraphNodeView] | None = None,
        edges: list[GraphEdgeView] | None = None,
        mode: GraphMode = GraphMode.RUN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._graph_nodes: list[GraphNodeView] = nodes or []
        self._edges: list[GraphEdgeView] = edges or []
        self._viewport = GraphViewport(mode=mode)
        self._renderer = AsciiGraphRenderer()

    def render(self) -> str:
        """Return rendered graph string.

        Falls back to text adjacency list when not in a TTY (non-interactive).
        """
        text_fallback = not sys.stdout.isatty()
        w = self._viewport.effective_width(80)
        h = self._viewport.effective_height(24)
        self._renderer.width = w
        self._renderer.height = h
        return self._renderer.render(
            self._graph_nodes,
            self._edges,
            text_fallback=text_fallback,
        )

    def load_view_state(self, view_state: GraphViewState) -> None:
        """Load a GraphViewState into the canvas."""
        self._graph_nodes = view_state.nodes
        self._edges = view_state.edges
        self._viewport = GraphViewport(mode=view_state.mode)
        try:
            self.refresh()
        except Exception:
            pass

    def action_pan_up(self) -> None:
        self._viewport = self._viewport.pan(0, -1)
        self.refresh()

    def action_pan_down(self) -> None:
        self._viewport = self._viewport.pan(0, 1)
        self.refresh()

    def action_pan_left(self) -> None:
        self._viewport = self._viewport.pan(-1, 0)
        self.refresh()

    def action_pan_right(self) -> None:
        self._viewport = self._viewport.pan(1, 0)
        self.refresh()

    def action_zoom_in(self) -> None:
        self._viewport = self._viewport.zoom_in()
        self.refresh()

    def action_zoom_out(self) -> None:
        self._viewport = self._viewport.zoom_out()
        self.refresh()

    def action_mode_run(self) -> None:
        self._viewport = self._viewport.set_mode(GraphMode.RUN)
        self.refresh()

    def action_mode_kg(self) -> None:
        self._viewport = self._viewport.set_mode(GraphMode.KG)
        self.refresh()

    def action_mode_memory(self) -> None:
        self._viewport = self._viewport.set_mode(GraphMode.MEMORY)
        self.refresh()

    def action_mode_context(self) -> None:
        self._viewport = self._viewport.set_mode(GraphMode.CONTEXT)
        self.refresh()

    def action_mode_impact(self) -> None:
        self._viewport = self._viewport.set_mode(GraphMode.IMPACT)
        self.refresh()
