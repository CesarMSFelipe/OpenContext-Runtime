from __future__ import annotations

from opencontext_core.context.assembler import PromptAssembler


def test_stable_section_ordering_and_token_estimates() -> None:
    prompt = PromptAssembler().assemble(
        "Where is auth?",
        [],
        tool_schemas="tool schema",
        project_manifest="manifest",
        repo_map="repo map",
    )

    names = [section.name for section in prompt.sections]
    assert names[:7] == [
        "system",
        "instructions",
        "tool_schemas",
        "provider_policy_summary",
        "project_manifest",
        "repo_map",
        "workflow_contract",
    ]
    assert names[-1] == "current_user_input"
    assert all(section.tokens >= 0 for section in prompt.sections)
    assert prompt.sections[0].stable is True


def test_prompt_assembler_redacts_user_input_before_prompt_sink() -> None:
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    prompt = PromptAssembler().assemble(f"explain {secret}", [])

    assert secret not in prompt.content
    current_input = [section for section in prompt.sections if section.name == "current_user_input"]
    assert current_input[0].redacted is True
