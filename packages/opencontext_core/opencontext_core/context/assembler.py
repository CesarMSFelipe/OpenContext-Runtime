"""Prompt assembly."""

from __future__ import annotations

from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.context.prompt_cache import PromptPrefixCachePlanner
from opencontext_core.models.context import (
    AssembledPrompt,
    ContextItem,
    ContextPriority,
    PromptSection,
)
from opencontext_core.safety.prompt_injection import (
    PromptInjectionScanner,
    render_untrusted_context,
)
from opencontext_core.safety.redaction import SinkGuard


class PromptAssembler:
    """Builds a deterministic prompt from request and selected context."""

    def assemble(
        self,
        user_request: str,
        context_items: list[ContextItem],
        *,
        instructions: str = "",
        tool_schemas: str = "",
        provider_policy_summary: str = "",
        project_manifest: str = "",
        repo_map: str = "",
        workflow_contract: str = "",
        memory: str = "",
        conversation: str = "",
    ) -> AssembledPrompt:
        """Assemble a prompt with traceable sections."""

        context_lines = []
        scanner = PromptInjectionScanner()
        sink_guard = SinkGuard()
        safe_user_request, user_redacted = sink_guard.redact(user_request)
        user_findings = scanner.scan(safe_user_request)
        if user_findings:
            safe_user_request = f"[INJECTION_WARNING:{len(user_findings)}]\n{safe_user_request}"
        for index, item in enumerate(context_items, start=1):
            redacted_content, redacted = sink_guard.redact(item.content)
            rendered_content = render_untrusted_context(
                item.source,
                item.classification.value,
                redacted_content,
            )
            findings = scanner.scan(redacted_content)
            if findings:
                rendered_content = f"[INJECTION_WARNING:{len(findings)}]\n{rendered_content}"
            context_lines.append(
                "\n".join(
                    [
                        f"[{index}] source={item.source} type={item.source_type} "
                        f"priority={item.priority.name} score={item.score:.4f} redacted={redacted}",
                        rendered_content,
                    ]
                )
            )
        context_content, retrieved_redacted = sink_guard.redact(
            "\n\n".join(context_lines) if context_lines else "No project context selected."
        )
        sections = [
            _section(
                sink_guard,
                name="system",
                content=(
                    "You are using OpenContext Runtime. Answer from selected context, "
                    "state uncertainty, and avoid inventing project facts."
                ),
                stable=True,
                priority=ContextPriority.P0,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="instructions",
                content=instructions or "No additional trusted instructions selected.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="tool_schemas",
                content=tool_schemas or "No tool schemas enabled.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="provider_policy_summary",
                content=provider_policy_summary or "Provider policy: mock/local only by default.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="project_manifest",
                content=project_manifest or "Project manifest summary unavailable.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="repo_map",
                content=repo_map or "Repository map unavailable.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="workflow_contract",
                content=workflow_contract
                or "Use the selected context and explain uncertainty when evidence is missing.",
                stable=True,
                priority=ContextPriority.P1,
                trusted=True,
            ),
            _section(
                sink_guard,
                name="memory",
                content=memory or "No additional project memory selected.",
                stable=False,
                priority=ContextPriority.P2,
            ),
            PromptSection(
                name="retrieved_context",
                content=context_content,
                stable=False,
                tokens=0,
                priority=ContextPriority.P1,
                redacted=retrieved_redacted,
            ),
            _section(
                sink_guard,
                name="conversation",
                content=conversation or "No prior conversation provided.",
                stable=False,
                priority=ContextPriority.P3,
            ),
            PromptSection(
                name="current_user_input",
                content=safe_user_request,
                stable=False,
                tokens=0,
                priority=ContextPriority.P0,
                redacted=user_redacted,
            ),
        ]
        measured_sections = [
            section.model_copy(update={"tokens": estimate_tokens(section.content)})
            for section in sections
        ]
        measured_sections = PromptPrefixCachePlanner().order_sections(measured_sections)
        prompt = "\n\n".join(
            f"## {section.name.replace('_', ' ').title()}\n{section.content}"
            for section in measured_sections
        )
        return AssembledPrompt(
            content=prompt,
            sections=measured_sections,
            total_tokens=estimate_tokens(prompt),
        )


def _section(
    sink_guard: SinkGuard,
    *,
    name: str,
    content: str,
    stable: bool,
    priority: ContextPriority,
    trusted: bool = False,
) -> PromptSection:
    safe_content, redacted = sink_guard.redact(content)
    return PromptSection(
        name=name,
        content=safe_content,
        stable=stable,
        tokens=0,
        priority=priority,
        trusted=trusted,
        redacted=redacted,
    )
