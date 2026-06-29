"""The seven named retrieval strategies + a dynamic selector (PR-010, §Retrieval Strategies).

Each strategy is a deterministic, stable re-ordering of an already-ranked
``list[ContextItem]`` — it floats the items the strategy favours to the front while
preserving the relative order of everything else (so MMR/relevance ordering is kept
within each band). ``symbol_first`` maps to the planner's existing name-anchored
symbol pass: symbol *definitions* lead. No strategy performs new I/O (design #3).

``select_strategy(node, intent)`` picks one per workflow node from the node name and
the task intent. The Context Harness calls it before retrieval.
"""

from __future__ import annotations

from collections.abc import Callable

from opencontext_core.models.context import ContextItem, RetrievalStrategy

# Symbol kinds that constitute a definition a developer opens to "add/modify X"
# (mirrors retrieval/planner.py:_DEFINITION_KINDS for the symbol_first band).
_DEFINITION_KINDS = frozenset(
    {"class", "function", "method", "interface", "trait", "struct", "enum", "constant"}
)


def _looks_like_test(source: str) -> bool:
    base = source.rsplit("/", 1)[-1].lower()
    return base.startswith("test_") or base.endswith("_test.py") or "/tests/" in source.lower()


def _is_symbol_definition(item: ContextItem) -> bool:
    if _looks_like_test(item.source):
        return False
    kind = str(item.metadata.get("symbol_kind", "")).lower()
    if kind in _DEFINITION_KINDS:
        return True
    return item.source_type in {"symbol", "code"}


def _is_owner(item: ContextItem) -> bool:
    src = item.source.lower()
    if item.source_type in {"owner", "codeowners"}:
        return True
    return "codeowners" in src or bool(item.metadata.get("owner"))


def _is_failure(item: ContextItem) -> bool:
    if item.source_type in {"diagnostic", "failure", "log", "stack_trace"}:
        return True
    text = item.content.lower()
    return any(
        marker in text
        for marker in ("traceback", "error:", "exception", "assertionerror", "failed")
    )


def _is_architecture(item: ContextItem) -> bool:
    src = item.source.lower()
    if item.source_type in {"architecture", "doc"}:
        return True
    return any(token in src for token in ("architecture", "/docs/", "design", "adr"))


def _is_decision(item: ContextItem) -> bool:
    src = item.source.lower()
    if item.source_type in {"decision", "memory"}:
        return True
    return "decision" in src or "adr" in src or bool(item.metadata.get("decision"))


def _is_command(item: ContextItem) -> bool:
    src = item.source.lower()
    if item.source_type in {"command", "tool", "shell"}:
        return True
    return any(
        token in src
        for token in ("makefile", "justfile", "/scripts/", ".sh", "pyproject.toml", "package.json")
    )


# Predicate per strategy: items satisfying it form the leading band.
_STRATEGY_PREDICATE: dict[RetrievalStrategy, Callable[[ContextItem], bool]] = {
    RetrievalStrategy.SYMBOL_FIRST: _is_symbol_definition,
    RetrievalStrategy.TEST_FIRST: lambda it: _looks_like_test(it.source),
    RetrievalStrategy.OWNER_FIRST: _is_owner,
    RetrievalStrategy.FAILURE_FIRST: _is_failure,
    RetrievalStrategy.ARCHITECTURE_FIRST: _is_architecture,
    RetrievalStrategy.DECISION_FIRST: _is_decision,
    RetrievalStrategy.COMMAND_FIRST: _is_command,
}


def reorder(items: list[ContextItem], strategy: RetrievalStrategy) -> list[ContextItem]:
    """Stably float the items the ``strategy`` favours to the front.

    Relevance order is preserved *within* each band (favoured vs. rest), so the
    strategy re-prioritizes which evidence class leads without discarding the
    planner's MMR/relevance ordering. Deterministic for a fixed input.
    """
    predicate = _STRATEGY_PREDICATE.get(strategy)
    if predicate is None:
        return list(items)
    leading = [it for it in items if predicate(it)]
    trailing = [it for it in items if not predicate(it)]
    return leading + trailing


# Node-name -> strategy. Substrings are matched so node ids like "local_inspection"
# or "gather_context" resolve. First match wins (order matters).
_NODE_STRATEGY: tuple[tuple[str, RetrievalStrategy], ...] = (
    ("diagnose", RetrievalStrategy.FAILURE_FIRST),
    ("inspection", RetrievalStrategy.TEST_FIRST),
    ("verify", RetrievalStrategy.TEST_FIRST),
    ("test", RetrievalStrategy.TEST_FIRST),
    ("escalation", RetrievalStrategy.OWNER_FIRST),
    ("design", RetrievalStrategy.ARCHITECTURE_FIRST),
    ("architecture", RetrievalStrategy.ARCHITECTURE_FIRST),
    ("propose", RetrievalStrategy.DECISION_FIRST),
    ("review", RetrievalStrategy.DECISION_FIRST),
    ("apply", RetrievalStrategy.COMMAND_FIRST),
    ("mutate", RetrievalStrategy.SYMBOL_FIRST),
    ("gather", RetrievalStrategy.SYMBOL_FIRST),
)

# Intent keyword -> strategy (overrides the node default when the task text is explicit).
_INTENT_STRATEGY: tuple[tuple[str, RetrievalStrategy], ...] = (
    ("debug", RetrievalStrategy.FAILURE_FIRST),
    ("failing", RetrievalStrategy.FAILURE_FIRST),
    ("traceback", RetrievalStrategy.FAILURE_FIRST),
    ("crash", RetrievalStrategy.FAILURE_FIRST),
    ("owner", RetrievalStrategy.OWNER_FIRST),
    ("who owns", RetrievalStrategy.OWNER_FIRST),
    ("architecture", RetrievalStrategy.ARCHITECTURE_FIRST),
    ("decision", RetrievalStrategy.DECISION_FIRST),
    ("command", RetrievalStrategy.COMMAND_FIRST),
    ("run the", RetrievalStrategy.COMMAND_FIRST),
)


def select_strategy(node: str, intent: str = "") -> RetrievalStrategy:
    """Select a retrieval strategy for a workflow node + task intent (book §Strategies).

    A debugging node selects ``failure_first``; a verify/inspection node selects
    ``test_first``. An explicit intent keyword overrides the node default. Falls back
    to ``symbol_first`` (symbol-before-file is the core principle).
    """
    node_l = node.strip().lower()
    intent_l = intent.strip().lower()

    # An explicit failure intent always wins (debugging dominates the node default).
    for keyword, strat in _INTENT_STRATEGY:
        if keyword in intent_l and strat is RetrievalStrategy.FAILURE_FIRST:
            return strat

    for fragment, strat in _NODE_STRATEGY:
        if fragment in node_l:
            return strat

    for keyword, strat in _INTENT_STRATEGY:
        if keyword in intent_l:
            return strat

    return RetrievalStrategy.SYMBOL_FIRST
