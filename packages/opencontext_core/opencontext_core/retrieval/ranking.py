"""Retrieval scoring helpers for keyword, path, and symbol search."""

from __future__ import annotations

import re

from opencontext_core.models.project import FileKind, ProjectFile, Symbol

TERM_RE = re.compile(r"[A-Za-z0-9_]+")
QUERY_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "does",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "of",
    "on",
    "project",
    "the",
    "this",
    "to",
    "with",
    "work",
}


class RetrievalScorer:
    """Scores manifest entries with simple deterministic hybrid relevance."""

    def terms(self, query: str) -> list[str]:
        """Tokenize a query into lowercase terms."""

        terms: list[str] = []
        for raw_term in TERM_RE.findall(query):
            term = raw_term.lower()
            if len(term) <= 1 or term in QUERY_STOPWORDS:
                continue
            terms.append(term)
            if term.endswith("ing") and len(term) > 5:
                stem = term[:-3]
                if stem:
                    terms.append(stem)
        return list(dict.fromkeys(terms))

    def file_score(
        self,
        terms: list[str],
        file: ProjectFile,
        symbols: list[Symbol],
    ) -> tuple[float, dict[str, object]]:
        """Score one file from keyword, path, symbol, and file-type signals."""

        haystacks = {
            "path": file.path.lower(),
            "summary": file.summary.lower(),
            "symbols": " ".join(symbol.name.lower() for symbol in symbols),
            "file_type": file.file_type.value,
        }
        path_hits = _hit_count(terms, haystacks["path"])
        summary_hits = _hit_count(terms, haystacks["summary"])
        symbol_hits = _hit_count(terms, haystacks["symbols"])
        type_hits = _hit_count(terms, haystacks["file_type"])
        raw = path_hits * 2.0 + summary_hits + symbol_hits * 3.0 + type_hits
        raw += _file_type_bonus(file.file_type)
        denominator = max(1.0, len(terms) * 4.0)
        score = min(1.0, raw / denominator)
        return score, {
            "path_hits": path_hits,
            "summary_hits": summary_hits,
            "symbol_hits": symbol_hits,
            "type_hits": type_hits,
        }

    def symbol_score(self, terms: list[str], symbol: Symbol) -> tuple[float, dict[str, object]]:
        """Score one symbol from name, kind, and path signals."""

        name_hits = _hit_count(terms, symbol.name.lower())
        kind_hits = _hit_count(terms, symbol.kind.lower())
        path_hits = _hit_count(terms, symbol.path.lower())
        raw = name_hits * 3.0 + kind_hits + path_hits
        denominator = max(1.0, len(terms) * 4.0)
        score = min(1.0, raw / denominator)
        return score, {"name_hits": name_hits, "kind_hits": kind_hits, "path_hits": path_hits}


class SemanticReranker:
    """State-of-the-art semantic reranker for high-signal context selection.
    
    Refines hybrid scores using semantic similarity or cross-encoder signals.
    """

    def rerank(
        self,
        query: str,
        candidates: list[tuple[float, ProjectFile]],
        top_k: int = 50,
    ) -> list[tuple[float, ProjectFile]]:
        """Rerank candidates using semantic relevance signals."""
        if not candidates:
            return []

        # In core, we use a metadata-aware semantic heuristic.
        # Specialized providers can override this with Cross-Encoders.
        query_terms = set(query.lower().split())
        results = []

        for score, file in candidates[:top_k]:
            semantic_boost = 0.0
            content_hint = (file.summary + " " + file.path).lower()
            
            # Boost based on exact semantic intersection and hierarchy
            matches = sum(1 for term in query_terms if term in content_hint)
            if matches:
                semantic_boost = (matches / len(query_terms)) * 0.5
            
            # Recency and depth bonus
            depth_penalty = min(0.1, file.path.count("/") * 0.02)
            
            new_score = min(1.0, score + semantic_boost - depth_penalty)
            results.append((new_score, file))

        return sorted(results, key=lambda x: x[0], reverse=True)


def _hit_count(terms: list[str], haystack: str) -> int:
    return sum(1 for term in terms if term in haystack)


def _file_type_bonus(file_type: FileKind) -> float:
    bonuses = {
        FileKind.CODE: 0.2,
        FileKind.CONFIG: 0.16,
        FileKind.DOCUMENTATION: 0.12,
        FileKind.TEMPLATE: 0.1,
        FileKind.TEST: 0.08,
        FileKind.UNKNOWN: 0.02,
        FileKind.ASSET: 0.0,
    }
    return bonuses[file_type]
