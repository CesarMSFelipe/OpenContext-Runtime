"""ContextContract and VerificationGate models for OpenContext Runtime v2."""

from __future__ import annotations

import hashlib
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from opencontext_core.models.evidence import EvidenceRef

RiskTier = Literal["cheap", "precise", "critical"]


class VerificationGate(BaseModel):
    """A gate that must pass before a context contract is considered verified."""

    id: str = Field(description="Unique gate identifier, e.g. 'run-tests'.")
    required: bool = Field(default=True, description="Whether this gate is mandatory.")
    passed: bool | None = Field(default=None, description="None = not yet evaluated.")


class ContractCoverage(BaseModel):
    """How much of a contract's required context was actually resolved.

    Fail-closed: an unresolved contract reads as low coverage, never a silent
    "complete". When nothing is required, coverage is trivially satisfied (1.0).
    """

    model_config = ConfigDict(extra="forbid")

    required_symbols: int = Field(default=0, ge=0)
    resolved_symbols: int = Field(default=0, ge=0)
    required_files: int = Field(default=0, ge=0)
    resolved_files: int = Field(default=0, ge=0)
    required_memories: int = Field(default=0, ge=0)
    resolved_memories: int = Field(default=0, ge=0)

    def ratio(self) -> float:
        """Fraction of required context resolved (1.0 when nothing required)."""
        required = self.required_symbols + self.required_files + self.required_memories
        if required == 0:
            return 1.0
        resolved = self.resolved_symbols + self.resolved_files + self.resolved_memories
        return min(1.0, resolved / required)

    def is_complete(self) -> bool:
        """True only when every required item was resolved."""
        return (
            self.resolved_symbols >= self.required_symbols
            and self.resolved_files >= self.required_files
            and self.resolved_memories >= self.required_memories
        )


class ContextContract(BaseModel):
    """Declarative contract describing what context a task requires and how to verify it."""

    schema_version: str = Field(default="opencontext.context_contract.v2")
    contract_id: str | None = Field(
        default=None,
        description="Stable id derived from task+type+tier; auto-filled if omitted.",
    )
    task: str = Field(description="Free-text task description.")
    task_type: str = Field(description="Classified task type (bugfix, feature, etc).")
    risk_level: str = Field(description="Risk level: low, medium, high.")
    risk_tier: RiskTier = Field(description="Budget tier: cheap, precise, or critical.")
    workflow_hint: str | None = Field(
        default=None, description="Target workflow, e.g. 'sdd' or 'quickfix'."
    )
    policy_profile: str | None = Field(
        default=None, description="Named tool/provider policy profile to apply."
    )
    quality_profile: str | None = Field(
        default=None, description="Named quality-gate profile to apply."
    )
    language: str | None = Field(default=None)
    framework: str | None = Field(default=None)
    known: list[EvidenceRef] = Field(default_factory=list)
    unknown: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    required_symbols: list[str] = Field(default_factory=list)
    required_files: list[str] = Field(default_factory=list)
    required_memories: list[str] = Field(default_factory=list)
    must_verify: list[VerificationGate] = Field(default_factory=list)
    forbidden_sources: list[str] = Field(default_factory=list)
    token_budget: int = Field(description="Maximum token budget for context assembly.")
    coverage: ContractCoverage | None = Field(
        default=None, description="Resolution coverage of required context (fail-closed)."
    )

    @model_validator(mode="after")
    def _fill_contract_id(self) -> ContextContract:
        """Derive a stable contract_id from identity fields when not supplied."""
        if self.contract_id is None:
            raw = f"{self.task}\x00{self.task_type}\x00{self.risk_tier}"
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
            self.contract_id = f"cc-{digest}"
        return self

    def is_complete(self) -> bool:
        """Return True only when required symbols/files AND must_verify are both non-empty."""
        has_sources = bool(self.required_symbols or self.required_files)
        has_gates = bool(self.must_verify)
        return has_sources and has_gates

    def to_yaml(self) -> str:
        """Serialize to human-readable YAML."""
        data = self.model_dump()
        # model_dump() already recursed nested models into dicts, so yaml.dump won't choke.
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
