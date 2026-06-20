"""Recursive summarization for memory rehydration.

Recall over-fetches candidate memory, then compresses it down to the prompt
budget so more signal fits the same tokens. The summary is produced by the cheap
``summarize`` role when a model is reachable, and by a deterministic
line-boundary trim otherwise — so rehydration still works (degraded) with no
model bound. Never raises: any model/gateway failure falls back to the trim.
"""

from __future__ import annotations

from typing import Any


def _trim_to_budget(text: str, target_tokens: int) -> str:
    """Keep whole lines (already ranked best-first) up to the token budget."""
    from opencontext_core.context.budgeting import estimate_tokens

    kept: list[str] = []
    for line in text.split("\n"):
        if kept and estimate_tokens("\n".join([*kept, line])) > target_tokens:
            break
        kept.append(line)
    return "\n".join(kept)


def summarize_to_budget(text: str, target_tokens: int, gateway: Any | None = None) -> str:
    """Compress ``text`` to ~``target_tokens``.

    Returns ``text`` unchanged when it already fits. With a gateway, asks the
    cheap ``summarize`` role to condense; falls back to a deterministic
    line-boundary trim when there is no gateway, the model is mock, or it errors.
    """
    from opencontext_core.context.budgeting import estimate_tokens

    if not text.strip() or estimate_tokens(text) <= target_tokens:
        return text

    if gateway is not None:
        try:
            from opencontext_core.models.llm import LLMRequest

            request = LLMRequest(
                prompt=(
                    f"Condense the following project memory to at most {target_tokens} "
                    "tokens. Keep decisions, constraints, and file references; drop "
                    f"repetition and chatter.\n\n{text}"
                ),
                provider="host",
                model="default",
                max_output_tokens=target_tokens,
                context_items=[],
                metadata={"role": "summarize", "task_complexity": "summarize"},
            )
            response = gateway.generate(request)
            out = (getattr(response, "content", "") or "").strip()
            is_real = getattr(response, "provider", "") != "mock" and not out.startswith(
                "Mock response"
            )
            if out and is_real:
                return out
        except Exception:
            pass

    return _trim_to_budget(text, target_tokens)
