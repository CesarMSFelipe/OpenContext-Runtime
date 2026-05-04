from __future__ import annotations

from datetime import datetime

from opencontext_core.compat import UTC
from opencontext_core.config import OpenContextConfig, default_config_data
from opencontext_core.context.budgeting import TokenBudgetManager
from opencontext_core.memory_usability import MemoryCandidateExtractor
from opencontext_core.models.trace import RuntimeTrace


def test_memory_candidate_extractor_extracts_token_validation() -> None:
    candidates = MemoryCandidateExtractor().extract(_trace())

    assert any(candidate.kind.value == "validation" for candidate in candidates)


def _trace() -> RuntimeTrace:
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
