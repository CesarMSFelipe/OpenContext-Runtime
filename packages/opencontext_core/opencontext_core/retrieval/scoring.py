"""Hybrid retrieval scoring — pure function, no side effects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RetrievalWeights:
    semantic_relevance: float = 0.25
    graph_centrality: float = 0.20
    call_distance: float = 0.15
    test_affinity: float = 0.10
    memory_confidence: float = 0.10
    recent_failure: float = 0.08
    risk_requirement: float = 0.07
    freshness: float = 0.03
    provenance: float = 0.02
    # Penalties
    stale_memory_penalty: float = 0.05
    token_cost_penalty: float = 0.03
    uncertainty_penalty: float = 0.02


def compute_hybrid_score(
    candidate_id: str,
    candidate_source: str,
    candidate_source_type: str,
    candidate_source_trust: float,
    candidate_modified_at: str | None,
    candidate_tokens: int,
    lexical_score: float,
    memory_boost_map: dict[str, float],
    graph_distance_map: dict[str, int],
    is_required: bool,
    is_test: bool,
    weights: RetrievalWeights | None = None,
    memory_confidence: float = 1.0,
    is_stale: bool = False,
    is_uncertain: bool = False,
) -> float:
    """Pure function. No side effects. Deterministic."""
    w = weights or RetrievalWeights()

    sem_rel = max(0.0, min(1.0, lexical_score))
    centrality = _normalize_distance(graph_distance_map.get(candidate_id, 999))
    call_dist = centrality
    test_aff = 1.0 if is_test else 0.0
    mem_conf = max(0.0, min(1.0, memory_confidence))
    fail_boost = max(0.0, min(1.0, memory_boost_map.get(candidate_id, 0.0)))
    risk_req = 1.0 if is_required else 0.0
    fresh = _compute_freshness(candidate_modified_at)
    prov = max(0.0, min(1.0, candidate_source_trust))

    positive = (
        sem_rel * w.semantic_relevance
        + centrality * w.graph_centrality
        + call_dist * w.call_distance
        + test_aff * w.test_affinity
        + mem_conf * w.memory_confidence
        + fail_boost * w.recent_failure
        + risk_req * w.risk_requirement
        + fresh * w.freshness
        + prov * w.provenance
    )
    penalty = (
        (w.stale_memory_penalty if is_stale else 0.0)
        + w.token_cost_penalty * min(1.0, candidate_tokens / 10_000)
        + (w.uncertainty_penalty if is_uncertain else 0.0)
    )
    return max(0.0, positive - penalty)


def _normalize_distance(distance: int) -> float:
    """0→1.0, 1→0.8, 2→0.6, 3→0.4, 4→0.2, 5+→0.0"""
    return max(0.0, 1.0 - distance * 0.2)


def _compute_freshness(modified_at: str | None) -> float:
    if not modified_at:
        return 0.7
    try:
        dt = datetime.fromisoformat(modified_at)
        days = (datetime.utcnow() - dt).days
        return max(0.5, 1.0 - days * 0.01)
    except (ValueError, TypeError):
        return 0.7
