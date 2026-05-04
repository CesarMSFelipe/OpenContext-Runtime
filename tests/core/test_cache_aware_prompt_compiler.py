from __future__ import annotations

from opencontext_core.models.context import ContextPriority, PromptSection
from opencontext_core.operating_model import CacheAwarePromptCompiler


def test_cache_aware_prompt_compiler_counts_stable_prefix() -> None:
    sections = [
        PromptSection(name="current_user_input", content="dynamic", stable=False, tokens=1),
        PromptSection(
            name="system",
            content="stable",
            stable=True,
            tokens=2,
            priority=ContextPriority.P0,
        ),
    ]

    plan = CacheAwarePromptCompiler().plan(sections)

    assert plan.stable_prefix_tokens == 2
    assert plan.cache_breaking_sections == ["current_user_input"]
