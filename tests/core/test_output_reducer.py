"""Tests for OutputReducer — output token reduction."""

from __future__ import annotations

from opencontext_core.compression.output_reducer import OutputReducer


def test_build_verbosity_instruction_returns_nonempty() -> None:
    reducer = OutputReducer()
    instruction = reducer.build_verbosity_instruction()
    assert isinstance(instruction, str)
    assert len(instruction) > 10


def test_holdout_fraction_one_always_holdout() -> None:
    reducer = OutputReducer(holdout_fraction=1.0)
    plan = reducer.plan(session_id="any-session")
    assert plan.is_holdout is True
    assert plan.verbosity_appended is False


def test_holdout_fraction_zero_never_holdout() -> None:
    reducer = OutputReducer(holdout_fraction=0.0)
    plan = reducer.plan(session_id="any-session")
    assert plan.is_holdout is False
    assert plan.verbosity_appended is True


def test_resume_turn_gets_reduced_effort() -> None:
    reducer = OutputReducer(holdout_fraction=0.0, effort_routing=True)
    plan = reducer.plan(last_tool_result="test passed exit code 0")
    assert plan.target_effort == "reduced"


def test_error_turn_gets_full_effort() -> None:
    reducer = OutputReducer(holdout_fraction=0.0, effort_routing=True)
    plan = reducer.plan(has_error=True)
    assert plan.target_effort == "full"


def test_stats_tracks_turns() -> None:
    reducer = OutputReducer(holdout_fraction=0.0)
    reducer.plan()
    reducer.plan()
    assert reducer.stats["total_turns"] == 2
    assert reducer.stats["treated_turns"] == 2
