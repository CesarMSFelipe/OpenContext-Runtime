"""REQ-05: planner.plan() must not return OC-generated files as context.

Tests the _is_oc_generated helper and verifies the retrieval filter removes
OC-artifact paths from plan() results.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Unit tests for the _is_oc_generated predicate
# ---------------------------------------------------------------------------


def test_is_oc_generated_mcp_json():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated(".mcp.json")
    assert _is_oc_generated("./.mcp.json")


def test_is_oc_generated_claude_oc_agent():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated(".claude/agents/oc-orchestrator.md")
    assert _is_oc_generated(".claude/agents/oc-planner.md")


def test_is_oc_generated_delegates():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated(".claude/agents/.opencontext-delegates/oc-apply.md")


def test_is_oc_generated_oc_commands():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated(".claude/commands/oc-new.md")


def test_is_oc_generated_opencontext_yaml():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated("opencontext.yaml")


def test_is_oc_generated_harness_yaml():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated("harness.yaml")


def test_is_oc_generated_receipt_json():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert _is_oc_generated("openspec/changes/my-change/receipt.json")


def test_is_oc_generated_does_not_match_user_files():
    from opencontext_core.retrieval.planner import _is_oc_generated

    assert not _is_oc_generated("src/auth.py")
    assert not _is_oc_generated("README.md")
    assert not _is_oc_generated(".claude/CLAUDE.md")
    assert not _is_oc_generated(".claude/agents/my-custom-agent.md")
    assert not _is_oc_generated("config.yaml")


# ---------------------------------------------------------------------------
# Integration test: plan() result contains no OC-generated paths
# ---------------------------------------------------------------------------


def test_plan_excludes_oc_generated_files(tmp_path):
    """plan() must filter out OC-generated items even if they are in the index."""
    from unittest.mock import MagicMock

    from opencontext_core.models.context import ContextItem, ContextPriority
    from opencontext_core.retrieval.contracts import EvidenceRequest, RetrievalSurface
    from opencontext_core.retrieval.planner import RetrievalPlanner

    oc_sources = [
        ".mcp.json",
        ".claude/agents/oc-orchestrator.md",
        "opencontext.yaml",
        "harness.yaml",
    ]
    user_sources = [
        "src/auth.py",
        "src/models.py",
    ]

    all_items = []
    for path in oc_sources + user_sources:
        item = ContextItem(
            id=path,
            source=path,
            source_type="file",
            content=f"content of {path}",
            tokens=10,
            priority=ContextPriority.P1,
            score=0.9,
        )
        all_items.append(item)

    # Build a minimal planner with a mock source.
    mock_source = MagicMock()
    mock_source.name = "mock"
    mock_source.retrieve.return_value = all_items

    planner = RetrievalPlanner([mock_source])

    request = EvidenceRequest(
        query="authenticate user",
        surface=RetrievalSurface.CLI,
        root=tmp_path,
        max_tokens=8000,
    )

    plan = planner.plan(request, top_k=20)
    result_sources = {item.source for item in plan.evidence}

    for oc_path in oc_sources:
        assert oc_path not in result_sources, (
            f"OC-generated path {oc_path!r} appeared in plan() results"
        )

    for user_path in user_sources:
        assert user_path in result_sources, (
            f"User file {user_path!r} was incorrectly filtered from plan() results"
        )
