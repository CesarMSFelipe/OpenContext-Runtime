"""ContextDAG scaffolding for traceable summaries and expansions."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ContextSourceRef(BaseModel):
    """Reference to original context that can be expanded under policy."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(description="Source item or trace identifier.")
    span: tuple[int, int] | None = Field(default=None, description="Optional character span.")


class ContextDAGNode(BaseModel):
    """Node in a context DAG."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Node id.")
    kind: str = Field(description="Node kind.")
    content: str = Field(description="Redacted node content.")
    source_refs: list[ContextSourceRef] = Field(
        default_factory=list,
        description="Expansion source refs.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Node metadata.")


class ContextSummaryNode(ContextDAGNode):
    """Summary node in a context DAG."""

    quality_score: float = Field(ge=0.0, le=1.0, description="Summary quality score.")


class ContextDAGEdge(BaseModel):
    """Directed relationship between context DAG nodes."""

    model_config = ConfigDict(extra="forbid")

    parent_id: str = Field(description="Parent node id.")
    child_id: str = Field(description="Child node id.")
    relation: str = Field(description="Relationship label.")


class ContextDAG(BaseModel):
    """DAG of raw context nodes and compact summary nodes."""

    model_config = ConfigDict(extra="forbid")

    nodes: list[ContextDAGNode] = Field(default_factory=list, description="DAG nodes.")
    edges: list[ContextDAGEdge] = Field(default_factory=list, description="DAG edges.")

    def add_node(self, node: ContextDAGNode) -> ContextDAG:
        """Return a DAG with one additional node."""

        return self.model_copy(update={"nodes": [*self.nodes, node]})

    def add_edge(self, edge: ContextDAGEdge) -> ContextDAG:
        """Return a DAG with one additional edge."""

        return self.model_copy(update={"edges": [*self.edges, edge]})
