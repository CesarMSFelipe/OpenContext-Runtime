"""Compact repository map generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.models.project import FileKind, ProjectManifest, RepoMap, RepoMapEntry, Symbol
from opencontext_core.retrieval.ranking import RetrievalScorer


class RepoMapEngine:
    """Builds and renders compact repository maps without full file contents."""

    def __init__(self) -> None:
        self.scorer = RetrievalScorer()

    def build(self, manifest: ProjectManifest, query: str | None = None) -> RepoMap:
        """Build a repo map from project manifest symbols and file metadata."""

        terms = self.scorer.terms(query or "")
        symbols_by_path = _symbols_by_path(manifest.symbols)
        entries: list[RepoMapEntry] = []
        for file in manifest.files:
            if file.file_type is FileKind.ASSET:
                continue
            symbols = symbols_by_path.get(file.path, [])
            relevance, metadata = self._score_entry(file.path, symbols, terms, file.file_type)
            rendered = self._render_entry(file.path, symbols)
            entries.append(
                RepoMapEntry(
                    file_path=file.path,
                    symbols=symbols,
                    token_estimate=estimate_tokens(rendered),
                    relevance_score=relevance,
                    metadata=metadata,
                )
            )
        ranked_entries = sorted(
            entries,
            key=lambda entry: (
                -entry.relevance_score,
                -int(bool(entry.symbols)),
                entry.token_estimate,
                entry.file_path,
            ),
        )
        return RepoMap(
            project_name=manifest.project_name,
            entries=ranked_entries,
            token_estimate=sum(entry.token_estimate for entry in ranked_entries),
            generated_at=datetime.now(tz=UTC),
        )

    def render(self, repo_map: RepoMap, max_tokens: int | None = None) -> str:
        """Render a repo map, optionally under a token budget."""

        rendered_entries: list[str] = []
        for entry in repo_map.entries:
            entry_text = self._render_entry(entry.file_path, entry.symbols)
            candidate_entries = [*rendered_entries, entry_text]
            candidate_text = "\n\n".join(candidate_entries)
            candidate_tokens = estimate_tokens(candidate_text)
            if max_tokens is not None and candidate_tokens > max_tokens:
                continue
            rendered_entries.append(entry_text)
        return "\n\n".join(rendered_entries)

    def _score_entry(
        self,
        path: str,
        symbols: list[Symbol],
        terms: list[str],
        file_type: FileKind,
    ) -> tuple[float, dict[str, object]]:
        path_lower = path.lower()
        symbol_text = " ".join(symbol.name.lower() for symbol in symbols)
        path_hits = sum(1 for term in terms if term in path_lower)
        symbol_hits = sum(1 for term in terms if term in symbol_text)
        structural_file = _is_structural_file(path, file_type)
        raw = path_hits * 2.0 + symbol_hits * 3.0 + (1.25 if structural_file else 0.0)
        if not terms and symbols:
            raw += 0.5
        score = min(1.0, raw / max(1.0, len(terms) * 4.0 if terms else 1.0))
        return score, {
            "path_hits": path_hits,
            "symbol_hits": symbol_hits,
            "structural_file": structural_file,
        }

    def _render_entry(self, file_path: str, symbols: list[Symbol]) -> str:
        lines = [file_path]
        if not symbols:
            return "\n".join(lines)
        class_symbols = {symbol.name for symbol in symbols if symbol.kind in {"class", "interface"}}
        emitted_containers: set[str] = set()
        for symbol in symbols:
            if symbol.kind in {"class", "interface", "trait", "enum"}:
                lines.append(f"  {symbol.kind} {symbol.name}")
                emitted_containers.add(symbol.name)
                for child in symbols:
                    if child.container == symbol.name:
                        lines.append(f"    + {child.name}")
            elif symbol.container is None:
                prefix = "  +" if symbol.name not in class_symbols else "  "
                lines.append(f"{prefix} {symbol.name}")
            elif symbol.container not in emitted_containers:
                lines.append(f"  {symbol.container}")
                lines.append(f"    + {symbol.name}")
                emitted_containers.add(symbol.container)
        return "\n".join(lines)


def _symbols_by_path(symbols: list[Symbol]) -> dict[str, list[Symbol]]:
    by_path: dict[str, list[Symbol]] = {}
    for symbol in symbols:
        by_path.setdefault(symbol.path, []).append(symbol)
    return by_path


def _is_structural_file(path: str, file_type: FileKind) -> bool:
    normalized = Path(path).as_posix().lower()
    structural_markers = (
        "config/",
        "settings",
        "schema",
        "route",
        "routes",
        "controller",
        "service",
        "repository",
        "entity",
        "middleware",
        "handler",
        "adapter",
    )
    return file_type is FileKind.CONFIG or any(
        marker in normalized for marker in structural_markers
    )
