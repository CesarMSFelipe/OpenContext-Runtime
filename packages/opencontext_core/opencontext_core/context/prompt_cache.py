"""Prompt prefix cache planning."""

from __future__ import annotations

from opencontext_core.models.context import PromptSection

PREFIX_SECTION_ORDER: tuple[str, ...] = (
    "system",
    "instructions",
    "tool_schemas",
    "provider_policy_summary",
    "project_manifest",
    "repo_map",
    "workflow_contract",
    "memory",
    "retrieved_context",
    "conversation",
    "current_user_input",
)


class PromptPrefixCachePlanner:
    """Orders prompt sections so stable provider-cache prefixes come first."""

    def order_sections(self, sections: list[PromptSection]) -> list[PromptSection]:
        """Return sections in cache-friendly prompt order."""

        index = {name: position for position, name in enumerate(PREFIX_SECTION_ORDER)}
        return sorted(
            sections,
            key=lambda section: (
                index.get(section.name, len(PREFIX_SECTION_ORDER)),
                not section.stable,
                int(section.priority),
                section.name,
            ),
        )
