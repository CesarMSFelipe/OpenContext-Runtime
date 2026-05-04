"""Trace harvesting for session memory."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.memory_usability.context_repository import ContextRepository, MemoryItem
from opencontext_core.memory_usability.memory_candidates import MemoryCandidate, MemoryKind
from opencontext_core.memory_usability.novelty_gate import NoveltyGate
from opencontext_core.models.context import DataClassification
from opencontext_core.models.trace import RuntimeTrace
from opencontext_core.safety.redaction import SinkGuard


class HarvestResult(BaseModel):
    """Result of harvesting memory candidates from a trace."""

    model_config = ConfigDict(extra="forbid")

    candidates: list[MemoryCandidate] = Field(description="Extracted redacted candidates.")
    stored: list[MemoryItem] = Field(description="Memory items stored after policy checks.")
    skipped: dict[str, str] = Field(description="Candidate content to skip reason.")
    approval_required: bool = Field(description="Whether storage is waiting for approval.")


class MemoryCandidateExtractor:
    """Extracts reusable facts, decisions, errors, and validation notes from traces."""

    def extract(self, trace: RuntimeTrace) -> list[MemoryCandidate]:
        """Extract deterministic memory candidates from sanitized trace metadata."""

        guard = SinkGuard()
        candidates: list[MemoryCandidate] = []
        source = f"trace:{trace.run_id}"
        selected_sources = [
            str(item.source) for item in trace.selected_context_items[:8] if item.source
        ]
        if selected_sources:
            content = "Selected context sources: " + ", ".join(selected_sources)
            candidates.append(_candidate(guard.redact(content)[0], source, MemoryKind.SUMMARY))
        if trace.errors:
            content = "Workflow errors: " + "; ".join(trace.errors)
            candidates.append(_candidate(guard.redact(content)[0], source, MemoryKind.ERROR))
        for key, value in sorted(trace.token_estimates.items()):
            if key in {"final_context_pack", "selected_after_optimization", "prompt"}:
                content = f"Token estimate {key} was {value}."
                candidates.append(_candidate(content, source, MemoryKind.VALIDATION))
        policy = trace.metadata.get("provider_policy_decision")
        if isinstance(policy, dict):
            content = f"Provider policy decision: {policy.get('reason', 'unknown')}."
            candidates.append(_candidate(guard.redact(content)[0], source, MemoryKind.DECISION))
        return candidates


class SessionMemoryRecorder:
    """Harvests session memory while preserving approval and redaction rules."""

    def __init__(
        self,
        repository: ContextRepository,
        *,
        require_approval: bool = True,
        novelty_gate: NoveltyGate | None = None,
    ) -> None:
        self.repository = repository
        self.require_approval = require_approval
        self.novelty_gate = novelty_gate or NoveltyGate()
        self.extractor = MemoryCandidateExtractor()

    def harvest(self, trace: RuntimeTrace) -> HarvestResult:
        """Extract, deduplicate, and optionally store trace-derived memory."""

        candidates = self.extractor.extract(trace)
        existing = [item.content for item in self.repository.list_items(include_archive=True)]
        stored: list[MemoryItem] = []
        skipped: dict[str, str] = {}
        for candidate in candidates:
            decision = self.novelty_gate.evaluate(candidate, existing)
            if not decision.accepted:
                skipped[candidate.content] = decision.reason
                continue
            if self.require_approval:
                skipped[candidate.content] = "approval_required"
                continue
            stored.append(
                self.repository.store(
                    candidate.content,
                    kind=candidate.kind.value,
                    source=candidate.source,
                    classification=candidate.classification,
                )
            )
        return HarvestResult(
            candidates=candidates,
            stored=stored,
            skipped=skipped,
            approval_required=self.require_approval,
        )


def _candidate(content: str, source: str, kind: MemoryKind) -> MemoryCandidate:
    return MemoryCandidate(
        content=content,
        source=source,
        kind=kind,
        novelty_score=0.7,
        reuse_likelihood=0.65,
        classification=DataClassification.INTERNAL,
        token_cost=estimate_tokens(content),
        source_trust=0.7,
    )
