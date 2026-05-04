from __future__ import annotations

from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.budgeting import TokenBudgetManager
from opencontext_core.memory_usability import ContextRepository, SessionMemoryRecorder
from opencontext_core.models.trace import RuntimeTrace


def test_harvest_redacts_secrets(tmp_path: Path) -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    config = OpenContextConfig.model_validate(default_config_data())
    trace = RuntimeTrace(
        run_id="run-secret",
        workflow_name="workflow",
        input="question",
        provider="mock",
        model="mock",
        selected_context_items=[],
        discarded_context_items=[],
        token_budget=TokenBudgetManager(config.context).calculate(),
        token_estimates={},
        compression_strategy="extractive_head_tail",
        prompt_sections=[],
        final_answer="done",
        errors=[f"failed with {secret}"],
        created_at=datetime.now(tz=UTC),
        metadata={},
    )

    recorder = SessionMemoryRecorder(ContextRepository(tmp_path), require_approval=False)
    result = recorder.harvest(trace)

    assert result.candidates
    assert all(secret not in candidate.content for candidate in result.candidates)
    assert all(secret not in item.content for item in result.stored)
