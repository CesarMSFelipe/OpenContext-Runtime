"""OutputReducer — reduce tokens the LLM writes back.

Two independent mechanisms:

A. Verbosity steering — append a terseness instruction to the system prompt
   so the model writes less. Does NOT touch the stable prefix (KV cache OK).

B. Effort routing — dial thinking effort DOWN on tool-result turns
   (file read, passing test, search result) where the model just resumes;
   keep FULL effort on new questions or errors.

A holdout fraction leaves a control group for measuring real savings.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any

# Default verbosity instruction (concise, no preamble, no code restatement)
_DEFAULT_VERBOSITY = (
    "Be concise. Omit recaps of code already visible in context. "
    "Avoid preambles like 'Sure' or 'Let me'. Answer directly. "
    "Do not restate the user's question before answering."
)

# Tool-result patterns that indicate a "resume" turn (low effort needed)
_RESUME_PATTERNS = (
    "file read",
    "search result",
    "test passed",
    "test ok",
    "exit code 0",
    "fetched",
    "grep result",
    "glob result",
)

# Patterns that indicate a new question or error (full effort needed)
_FULL_EFFORT_PATTERNS = (
    "error",
    "traceback",
    "failed",
    "exit code",
    "what",
    "how",
    "why",
    "implement",
    "fix",
    "change",
)


@dataclass
class OutputReductionPlan:
    """What the OutputReducer decided for this turn."""

    verbosity_appended: bool
    effort_routed: bool  # True when effort was actively managed
    target_effort: str  # "full" | "reduced" | "auto"
    is_holdout: bool  # True when this turn is in the control group
    savings_estimated_pct: float = 0.0


class OutputReducer:
    """Reduce output token consumption.

    Does NOT modify the user's request or the tool outputs — only the
    system/hidden instructions that control the model's response style.
    """

    def __init__(
        self,
        *,
        verbosity_instruction: str = _DEFAULT_VERBOSITY,
        effort_routing: bool = True,
        holdout_fraction: float = 0.1,
        seed: int = 42,
    ) -> None:
        self._verbosity_instruction = verbosity_instruction.strip()
        self._effort_routing = effort_routing
        self._holdout_fraction = holdout_fraction
        self._rng = random.Random(seed)
        self._turn_count = 0
        self._holdout_count = 0
        self._treated_count = 0

    def should_holdout(self, session_id: str = "") -> bool:
        """Deterministic holdout decision based on session_id.

        Using a hash of session_id ensures the same session always gets
        the same treatment (holdout vs shaped), so measurements are clean.
        """
        if self._holdout_fraction <= 0.0:
            return False
        if not session_id:
            # Fallback: random (non-deterministic but still controlled)
            return self._rng.random() < self._holdout_fraction
        h = int(hashlib.md5(session_id.encode()).hexdigest()[:8], 16)
        return (h % 1000) / 1000.0 < self._holdout_fraction

    def plan(
        self,
        *,
        user_input: str = "",
        last_tool_result: str = "",
        session_id: str = "",
        is_new_question: bool = False,
        has_error: bool = False,
    ) -> OutputReductionPlan:
        """Decide what output reduction to apply for this turn.

        Args:
            user_input: The user's current message.
            last_tool_result: The last tool output (if resuming after a tool).
            session_id: Stable session ID for holdout assignment.
            is_new_question: Whether this is a fresh question (vs tool resume).
            has_error: Whether the last result was an error.

        Returns:
            Plan describing what reduction to apply.
        """
        self._turn_count += 1

        # Holdout: skip shaping entirely for this session
        is_holdout = self.should_holdout(session_id)
        if is_holdout:
            self._holdout_count += 1
            return OutputReductionPlan(
                verbosity_appended=False,
                effort_routed=False,
                target_effort="auto",
                is_holdout=True,
                savings_estimated_pct=0.0,
            )

        self._treated_count += 1

        # Verbosity: always apply to shaped sessions
        verbosity = bool(self._verbosity_instruction)

        # Effort routing: determine level
        effort = "full"
        effort_routed = False
        if self._effort_routing:
            if has_error or is_new_question:
                effort = "full"
                effort_routed = True
            elif self._is_resume_turn(last_tool_result):
                effort = "reduced"
                effort_routed = True
            else:
                effort = "full"
                effort_routed = True

        # Estimate savings
        savings = 0.0
        if verbosity:
            savings += 15.0  # baseline: verbosity alone ~15%
        if effort == "reduced":
            savings += 15.0  # effort routing on resume turns ~15% more

        return OutputReductionPlan(
            verbosity_appended=verbosity,
            effort_routed=effort_routed,
            target_effort=effort,
            is_holdout=False,
            savings_estimated_pct=min(savings, 60.0),
        )

    def _is_resume_turn(self, tool_result: str) -> bool:
        """Detect if this turn is a resume after a tool result."""
        lower = tool_result.lower()
        for pattern in _RESUME_PATTERNS:
            if pattern in lower:
                return True
        # Check for patterns that indicate FULL effort
        for pattern in _FULL_EFFORT_PATTERNS:
            if pattern in lower:
                return False
        # If tool result is short and has no error markers, it's likely a resume
        return len(tool_result) < 500 and not any(
            e in lower for e in ("error", "fail", "traceback")
        )

    def build_verbosity_instruction(self) -> str:
        """Return the instruction to append to the system prompt.

        The caller should append this AFTER the system prompt proper
        (not inside the stable prefix for KV cache).
        """
        return self._verbosity_instruction

    def effort_hint(self, plan: OutputReductionPlan) -> dict[str, Any] | None:
        """Return a provider-specific effort hint.

        Anthropic: ``thinking`` config with ``budget_tokens``
        OpenAI: ``reasoning_effort`` parameter

        Returns None if no hint should be sent.
        """
        if plan.target_effort == "full":
            return None  # Let the provider decide default
        if plan.target_effort == "reduced":
            # Hint for reduced thinking/reasoning
            return {
                "type": "thinking",
                "budget_tokens": 128,  # minimum viable thinking
            }
        return None

    @property
    def stats(self) -> dict[str, int]:
        return {
            "total_turns": self._turn_count,
            "holdout_turns": self._holdout_count,
            "treated_turns": self._treated_count,
        }


__all__ = ["OutputReducer", "OutputReductionPlan"]
