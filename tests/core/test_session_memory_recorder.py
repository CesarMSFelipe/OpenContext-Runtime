from __future__ import annotations

from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.config import default_config_data
from opencontext_core.context.budgeting import TokenBudgetManager
from opencontext_core.memory_usability import ContextRepository, SessionMemoryRecorder
from opencontext_core.models.trace import RuntimeTrace


def test_session_memory_recorder_respects_approval(tmp_path: Path) -> None:
    trace = _trace()
    recorder = SessionMemoryRecorder(ContextRepository(tmp_path), require_approval=True)

    result = recorder.harvest(trace)

    assert result.candidates
    assert result.stored == []
    assert result.approval_required is True


def _trace() -> RuntimeTrace:
    from opencontext_core.config import OpenContextConfig

    config = OpenContextConfig.model_validate(default_config_data())
    return RuntimeTrace(
        run_id="run-1",
        workflow_name="context_pack.local",
        input="review auth",
        provider="local-only",
        model="none",
        selected_context_items=[],
        discarded_context_items=[],
        token_budget=TokenBudgetManager(config.context).calculate(),
        token_estimates={"final_context_pack": 10},
        compression_strategy="extractive_head_tail",
        prompt_sections=[],
        final_answer="done",
        created_at=datetime.now(tz=UTC),
        metadata={},
    )
