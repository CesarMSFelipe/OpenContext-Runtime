"""Tests for G1 — AGENTIC_SAFE preset (AC-G1-1, AC-G1-2)."""

from __future__ import annotations

from opencontext_core.agentic.config import BudgetMode, GitMode, MemoryMode, PresetId
from opencontext_core.agentic.presets import preset_config


def test_agentic_safe_preset_exists_and_loads() -> None:
    """AC-G1-1: PresetId.AGENTIC_SAFE resolves without error."""
    assert PresetId.AGENTIC_SAFE == "agentic-safe"
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config is not None
    assert config.preset == PresetId.AGENTIC_SAFE


def test_agentic_safe_budget_mode_is_warn() -> None:
    """AC-G1-2: SAFE preset must NOT use BudgetMode.STRICT."""
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config.budget_mode != BudgetMode.STRICT
    assert config.budget_mode == BudgetMode.WARN


def test_agentic_safe_git_mode_is_local_branch() -> None:
    """AC-G1-2: SAFE preset must NOT use GitMode.SINGLE_PR."""
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config.git_mode != GitMode.SINGLE_PR
    assert config.git_mode == GitMode.LOCAL_BRANCH


def test_agentic_safe_approval_before_apply_is_true() -> None:
    """AC-G1-2: SAFE preset must have approval_before_apply=True."""
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config.approval_before_apply is True


def test_agentic_safe_no_auto_archive() -> None:
    """AC-G1-2: SAFE preset must have allow_automatic_archive=False."""
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config.allow_automatic_archive is False


def test_agentic_safe_memory_mode_is_local() -> None:
    """AC-G1-2: SAFE preset must use MemoryMode.LOCAL."""
    config = preset_config(PresetId.AGENTIC_SAFE)
    assert config.memory_mode == MemoryMode.LOCAL


def test_agentic_safe_round_trips_model_validate() -> None:
    """AGENTIC_SAFE config survives a model_validate round-trip."""
    from opencontext_core.agentic.config import AgenticFlowConfig

    config = preset_config(PresetId.AGENTIC_SAFE)
    restored = AgenticFlowConfig.model_validate(config.model_dump())
    assert restored.preset == PresetId.AGENTIC_SAFE
    assert restored.budget_mode == BudgetMode.WARN
