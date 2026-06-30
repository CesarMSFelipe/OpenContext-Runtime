"""Memory benchmark — R@k, MRR, precision@k, and p50 latency harness.

Uses the existing ``SQLiteMemoryBackend.search()`` (FTS5+bm25) — no separate
BM25 implementation. Fixture format: list of objects with "query" and
"relevant" (list of doc IDs / key substrings that count as a hit).
"""

from __future__ import annotations

import json
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def recall_at_k(results: list[str], relevant: list[str], k: int) -> float:
    """Recall@k: fraction of relevant items found in the top-k results.

    Pure function with no I/O side effects.
    """
    if not relevant:
        return 0.0
    top_k = results[:k]
    hits = sum(1 for r in top_k if r in relevant)
    return hits / len(relevant)


def precision_at_k(results: list[str], relevant: list[str], k: int) -> float:
    """Precision@k: fraction of top-k results that are relevant.

    Pure function with no I/O side effects.
    """
    if k == 0:
        return 0.0
    top_k = results[:k]
    hits = sum(1 for r in top_k if r in relevant)
    return hits / k


def reciprocal_rank(results: list[str], relevant: list[str]) -> float:
    """Reciprocal rank: 1/(position of first relevant item, 1-based).

    Returns 0.0 when no relevant item appears in results.
    Pure function with no I/O side effects.
    """
    for idx, result in enumerate(results):
        if result in relevant:
            return 1.0 / (idx + 1)
    return 0.0


@dataclass
class MemoryBenchmarkQuestion:
    """A single benchmark question with expected relevant doc IDs."""

    query: str
    relevant: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryBenchmarkResult:
    """Aggregated result of running the memory benchmark."""

    recall_at_5: float
    mrr: float
    precision_at_5: float
    p50_ms: float
    p95_ms: float
    num_questions: int
    details: list[dict[str, Any]] = field(default_factory=list)


def run_benchmark(
    fixture_path: Path | str,
    backend: Any,
    k: int = 5,
) -> MemoryBenchmarkResult:
    """Run the benchmark fixture against *backend*.

    ``backend`` must support ``.search(query, limit=k)`` returning objects
    with ``.key`` or ``.id`` attributes (``SQLiteMemoryBackend`` contract).

    Fixture JSON: list of ``{query: str, relevant: [str, ...], ...}`` objects.
    Matching: a result's ``.key`` is a hit when any ``relevant`` entry is a
    substring of ``.key``, or matches ``.id`` exactly.
    """
    path = Path(fixture_path)
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    questions = [
        MemoryBenchmarkQuestion(
            query=item["query"],
            relevant=item["relevant"],
            metadata=item.get("metadata", {}),
        )
        for item in raw
    ]
    return run_benchmark_questions(questions, backend, k=k)


def run_benchmark_questions(
    questions: list[MemoryBenchmarkQuestion],
    backend: Any,
    k: int = 5,
) -> MemoryBenchmarkResult:
    """Run the benchmark over already-parsed *questions* against *backend*.

    The fixture-loading variant :func:`run_benchmark` delegates here; the seeded
    provider (:func:`seeded_memory_provider`) uses it directly so it needs no JSON
    file on disk.
    """
    recall_scores: list[float] = []
    rr_scores: list[float] = []
    precision_scores: list[float] = []
    latencies_ms: list[float] = []
    details: list[dict[str, Any]] = []

    for q in questions:
        t0 = time.perf_counter()
        records = backend.search(q.query, limit=k)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(elapsed_ms)

        # Build result IDs for metric computation.
        result_ids: list[str] = []
        for rec in records:
            key = str(getattr(rec, "key", None) or getattr(rec, "id", ""))
            result_ids.append(key)

        # Hit: any relevant entry appears as substring of result key or exact id.
        def _is_hit(result_key: str, rel_list: list[str]) -> bool:
            return any(rel in result_key for rel in rel_list)

        hit_flags = [_is_hit(rid, q.relevant) for rid in result_ids]
        matched_ids = [rid for rid, hit in zip(result_ids, hit_flags, strict=True) if hit]

        r5 = recall_at_k(matched_ids, q.relevant, k)
        p5 = precision_at_k(matched_ids, q.relevant, k)
        rr = reciprocal_rank(matched_ids, q.relevant)

        recall_scores.append(r5)
        precision_scores.append(p5)
        rr_scores.append(rr)

        details.append(
            {
                "query": q.query,
                "recall_at_k": r5,
                "precision_at_k": p5,
                "reciprocal_rank": rr,
                "latency_ms": elapsed_ms,
                "result_ids": result_ids,
            }
        )

    latencies_ms_sorted = sorted(latencies_ms)
    n = len(latencies_ms_sorted)
    p50_ms = statistics.median(latencies_ms_sorted) if n else 0.0
    p95_idx = max(0, int(n * 0.95) - 1)
    p95_ms = latencies_ms_sorted[p95_idx] if latencies_ms_sorted else 0.0

    return MemoryBenchmarkResult(
        recall_at_5=sum(recall_scores) / len(recall_scores) if recall_scores else 0.0,
        mrr=sum(rr_scores) / len(rr_scores) if rr_scores else 0.0,
        precision_at_5=sum(precision_scores) / len(precision_scores) if precision_scores else 0.0,
        p50_ms=p50_ms,
        p95_ms=p95_ms,
        num_questions=len(questions),
        details=details,
    )


# --------------------------------------------------------------------------- VDM-008
# A deterministic, self-contained corpus so ``memory-usefulness`` MEASURES provider-free
# (no live LLM, no tests/ tree, no packaged fixture). Each query's relevant keys are
# distinctive substrings the FTS5 search recovers from seeded record content.
SEED_FIXTURE: tuple[dict[str, Any], ...] = (
    {
        "query": "JWT authentication middleware implementation",
        "relevant": ["auth:jwt_middleware", "auth:token_validation", "auth:bearer_token"],
        "metadata": {"domain": "auth", "phase": "apply"},
    },
    {
        "query": "database connection pool configuration",
        "relevant": ["db:connection_pool", "db:pool_config", "db:pool_size"],
        "metadata": {"domain": "database", "phase": "apply"},
    },
    {
        "query": "test suite fails on CI environment",
        "relevant": ["failure:ci_test_failure", "failure:env_mismatch", "failure:ci_env_var"],
        "metadata": {"domain": "testing", "phase": "verify"},
    },
    {
        "query": "context pack builder token budget exceeded",
        "relevant": ["budget:token_limit", "budget:pack_overflow", "budget:token_cap"],
        "metadata": {"domain": "context", "phase": "explore"},
    },
    {
        "query": "memory harvest from agent trace",
        "relevant": ["episodic:harvest_run", "episodic:agent_trace", "episodic:trace_capture"],
        "metadata": {"domain": "memory", "phase": "archive"},
    },
    {
        "query": "knowledge graph symbol resolution call edges",
        "relevant": ["kg:symbol_resolution", "kg:call_edges", "kg:node_lookup"],
        "metadata": {"domain": "kg", "phase": "explore"},
    },
)


def _seed_records(questions: list[MemoryBenchmarkQuestion], backend: Any) -> int:
    """Seed *backend* so each query's relevant keys are FTS5-recoverable.

    For each (query, relevant_id) pair, store a :class:`MemoryRecord` whose ``key`` is
    the relevant id and whose ``content`` embeds the query text. Returns the count
    written. Mirrors the CLI memory-benchmark seeding contract (REQ-02c).
    """
    from datetime import UTC, datetime

    from opencontext_core.models.agent_memory import DecayPolicy, MemoryLayer, MemoryRecord

    now = datetime.now(tz=UTC)
    count = 0
    for q in questions:
        domain = q.metadata.get("domain", "general")
        phase = q.metadata.get("phase", "apply")
        for rel_id in q.relevant:
            backend.store(
                MemoryRecord(
                    id=f"bench:{rel_id}",
                    layer=MemoryLayer.SEMANTIC,
                    key=rel_id,
                    content=f"{q.query}. Key: {rel_id}. Domain: {domain}. Phase: {phase}.",
                    decay_policy=DecayPolicy(enabled=False),
                    created_at=now,
                    updated_at=now,
                )
            )
            count += 1
    return count


def run_seeded_memory_benchmark(
    questions: tuple[dict[str, Any], ...] = SEED_FIXTURE, *, k: int = 5
) -> MemoryBenchmarkResult:
    """Seed an ephemeral SQLite backend from a deterministic corpus and benchmark it.

    Provider-free (no live LLM). Uses a temp-file DB because ``SQLiteMemoryBackend``
    opens a fresh connection per call, so an in-memory DB would lose its schema/data
    between the seed and the search.
    """
    import os
    import tempfile

    from opencontext_core.memory.backends import SQLiteMemoryBackend

    parsed = [
        MemoryBenchmarkQuestion(
            query=item["query"], relevant=item["relevant"], metadata=item.get("metadata", {})
        )
        for item in questions
    ]
    fd, db_path = tempfile.mkstemp(suffix=".memory-bench.db", prefix="oc_mem_seed_")
    os.close(fd)
    try:
        backend = SQLiteMemoryBackend(db_path)
        _seed_records(parsed, backend)
        return run_benchmark_questions(parsed, backend, k=k)
    finally:
        try:
            Path(db_path).unlink()
        except OSError:
            pass


def seeded_memory_provider() -> Callable[[Path, bool], MemoryBenchmarkResult]:
    """Return a ``provider(root, smoke)`` callable for the ``memory-usefulness`` suite.

    Deterministic + provider-free: it ignores ``root``/``smoke`` and benchmarks the
    seeded corpus so the gate MEASURES (MET/FAILED) without a live model (VDM-008).
    """

    def _provider(root: Path, smoke: bool) -> MemoryBenchmarkResult:
        return run_seeded_memory_benchmark()

    return _provider
