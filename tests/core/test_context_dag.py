from __future__ import annotations

from opencontext_core.memory_usability import ContextDAG, ContextDAGEdge, ContextDAGNode


def test_context_dag_adds_nodes_and_edges() -> None:
    dag = ContextDAG().add_node(ContextDAGNode(id="raw-1", kind="raw", content="event"))
    dag = dag.add_node(ContextDAGNode(id="sum-1", kind="summary", content="summary"))
    dag = dag.add_edge(ContextDAGEdge(parent_id="raw-1", child_id="sum-1", relation="summarizes"))

    assert len(dag.nodes) == 2
    assert dag.edges[0].relation == "summarizes"
