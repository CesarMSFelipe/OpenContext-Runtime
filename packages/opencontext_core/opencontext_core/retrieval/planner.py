"""Unified retrieval planner for manifest and graph-backed evidence."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.indexing.context_builder import ContextBuilder, ContextNode
from opencontext_core.models.context import ContextItem, ContextPriority
from opencontext_core.models.project import ProjectManifest
from opencontext_core.retrieval.contracts import (
    EvidenceItem,
    EvidencePlan,
    EvidenceRequest,
    FreshnessStatus,
    RetrievalSurface,
    TrustDecision,
    evidence_trace_id,
)
from opencontext_core.retrieval.retriever import ProjectRetriever


class RetrievalSource(Protocol):
    """A source that can produce context candidates for a query."""

    name: str

    def retrieve(self, query: str, limit: int) -> list[ContextItem]:
        """Return up to ``limit`` context candidates for ``query``."""


class ManifestRetrievalSource:
    """Retrieval source backed by the existing manifest retriever."""

    name = "manifest"

    def __init__(self, manifest: ProjectManifest) -> None:
        self._retriever = ProjectRetriever(manifest)

    def retrieve(self, query: str, limit: int) -> list[ContextItem]:
        """Return manifest candidates with source metadata attached."""

        return [
            _with_source_metadata(item, self.name)
            for item in self._retriever.retrieve(query, limit)
        ]


class GraphRetrievalSource:
    """Retrieval source backed by the native SQLite knowledge graph."""

    name = "graph"

    def __init__(self, db_path: str | Path, root: str | Path) -> None:
        self.db_path = Path(db_path)
        self.root = Path(root)

    def retrieve(self, query: str, limit: int) -> list[ContextItem]:
        """Return graph-derived candidates with provenance and freshness metadata."""

        if limit <= 0:
            return []
        builder = ContextBuilder(db_path=self.db_path)
        try:
            context = builder.build_context(
                task=query,
                max_nodes=limit,
                include_code=True,
                root=self.root,
            )
            return [
                _context_node_to_item(
                    node,
                    db_path=self.db_path,
                    query=query,
                )
                for node in context.nodes[:limit]
            ]
        finally:
            builder.close()


class RetrievalPlanner:
    """Composes retrieval sources and returns deduplicated context candidates."""

    def __init__(
        self,
        manifest_or_sources: ProjectManifest | Sequence[RetrievalSource],
        *,
        graph_db_path: str | Path | None = None,
    ) -> None:
        if isinstance(manifest_or_sources, ProjectManifest):
            sources: list[RetrievalSource] = [ManifestRetrievalSource(manifest_or_sources)]
            if graph_db_path is not None:
                sources.append(GraphRetrievalSource(graph_db_path, manifest_or_sources.root))
            self.sources = sources
        else:
            self.sources = list(manifest_or_sources)
        self.omissions: list[str] = []

    def retrieve(self, query: str, top_k: int) -> list[ContextItem]:
        """Retrieve candidates from all sources without letting additive sources block fallback."""

        if top_k <= 0:
            return []

        candidates: list[ContextItem] = []
        self.omissions = []
        for source in self.sources:
            try:
                candidates.extend(source.retrieve(query, top_k))
            except Exception:
                if source.name == ManifestRetrievalSource.name:
                    raise
                self.omissions.append(f"{source.name}_unavailable")
                continue

        deduped = _deduplicate(candidates)
        return sorted(deduped, key=lambda item: (-item.score, item.tokens, item.id))[:top_k]

    def plan(self, request: EvidenceRequest, top_k: int) -> EvidencePlan:
        """Return a traceable evidence plan for a converged retrieval request."""

        context_items = self.retrieve(request.query, top_k)
        evidence = [_context_item_to_evidence(item, request.surface) for item in context_items]
        fallback_actions = _fallback_actions_for(request, evidence)
        trust_decision = _trust_decision(request, evidence, fallback_actions)
        return EvidencePlan(
            request=request,
            evidence=evidence,
            fallback_actions=fallback_actions,
            trust_decision=trust_decision,
            trace_id=evidence_trace_id(request, [item.id for item in evidence]),
            omissions=list(self.omissions),
            source_surfaces=_source_surfaces(evidence, request.surface),
        )


def _with_source_metadata(item: ContextItem, source_name: str) -> ContextItem:
    metadata = {**item.metadata, "retrieval_source": source_name}
    return item.model_copy(update={"metadata": metadata})


def _context_item_to_evidence(item: ContextItem, surface: RetrievalSurface) -> EvidenceItem:
    freshness = _freshness_from_metadata(item.metadata)
    provenance = {
        **item.metadata,
        "source": item.source,
        "source_type": item.source_type,
        "priority": item.priority.name,
    }
    return EvidenceItem(
        id=item.id,
        content=item.content,
        source=item.source,
        source_type=item.source_type,
        provenance=provenance,
        confidence=max(0.0, min(1.0, item.score if item.score > 0 else item.source_trust)),
        freshness=freshness,
        surface=surface,
        tokens=item.tokens,
        protected=bool(item.metadata.get("protected", False)),
        classification=item.classification,
    )


def _freshness_from_metadata(metadata: dict[str, object]) -> FreshnessStatus:
    value = metadata.get("freshness", FreshnessStatus.CURRENT.value)
    try:
        return FreshnessStatus(str(value))
    except ValueError:
        return FreshnessStatus.UNKNOWN


def _fallback_actions_for(request: EvidenceRequest, evidence: list[EvidenceItem]) -> list[str]:
    if request.risk_level.lower() != "high":
        return []
    insufficient = {
        FreshnessStatus.STALE,
        FreshnessStatus.UNKNOWN,
        FreshnessStatus.UNAVAILABLE,
    }
    return [f"read_source:{item.source}" for item in evidence if item.freshness in insufficient]


def _trust_decision(
    request: EvidenceRequest,
    evidence: list[EvidenceItem],
    fallback_actions: list[str],
) -> TrustDecision:
    if not evidence:
        return TrustDecision(status="insufficient", reason="no evidence available")
    if request.risk_level.lower() == "high" and fallback_actions:
        return TrustDecision(
            status="insufficient",
            reason="high-risk evidence requires explicit source fallback",
        )
    return TrustDecision(status="sufficient", reason="evidence freshness is acceptable")


def _source_surfaces(
    evidence: list[EvidenceItem],
    default_surface: RetrievalSurface,
) -> list[RetrievalSurface]:
    surfaces = list(dict.fromkeys(item.surface for item in evidence))
    return surfaces or [default_surface]


def _context_node_to_item(node: ContextNode, *, db_path: Path, query: str) -> ContextItem:
    content = _render_node_content(node)
    metadata = {
        "retrieval_source": "graph",
        "retrieval": {
            "query": query,
            "node": node.name,
            "kind": node.kind,
            "relationships": list(node.relationships),
        },
        "retrieval_rationale": _graph_rationale(node),
        "source_type": "graph",
        "freshness": "unknown",
        "graph_provenance": {
            "db_path": str(db_path),
            "file_path": node.file_path,
            "line": node.line,
            "relationships": list(node.relationships),
        },
        "symbol_kind": node.kind,
    }
    return ContextItem(
        id=f"graph:{node.file_path}:{node.line}:{node.name}",
        content=content,
        source=f"{node.file_path}:{node.line}",
        source_type="graph_symbol",
        priority=ContextPriority.P1,
        tokens=estimate_tokens(content),
        score=max(node.relevance_score, 0.0),
        metadata=metadata,
        trusted=True,
        source_trust=0.8,
    )


def _render_node_content(node: ContextNode) -> str:
    header = f"{node.kind} {node.name} in {node.file_path}:{node.line}"
    if node.source_code:
        return f"{header}\n{node.source_code}".strip()
    return header


def _graph_rationale(node: ContextNode) -> list[str]:
    rationale = [
        "source_type:graph",
        f"symbol_kind:{node.kind}",
        f"file:{node.file_path}",
    ]
    rationale.extend(f"relationship:{relationship}" for relationship in node.relationships)
    return rationale


def _deduplicate(items: list[ContextItem]) -> list[ContextItem]:
    by_id: dict[str, ContextItem] = {}
    for item in items:
        current = by_id.get(item.id)
        if current is None or item.score > current.score:
            by_id[item.id] = item
    return list(by_id.values())
