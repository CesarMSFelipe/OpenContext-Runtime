"""Performance, cache, model routing, and cost scaffolds."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.context.budgeting import estimate_tokens
from opencontext_core.context.prompt_cache import PromptPrefixCachePlanner
from opencontext_core.models.context import PromptSection


class CachePlan(BaseModel):
    """Cache-aware prompt plan."""

    model_config = ConfigDict(extra="forbid")

    stable_prefix_tokens: int = Field(ge=0, description="Stable prefix tokens.")
    dynamic_tokens: int = Field(ge=0, description="Dynamic section tokens.")
    cache_eligible_tokens: int = Field(ge=0, description="Tokens eligible for caching.")
    cache_breaking_sections: list[str] = Field(description="Dynamic sections.")
    recommended_order: list[str] = Field(description="Prompt section order.")
    estimated_cache_savings_tokens: int = Field(ge=0, description="Estimated reusable tokens.")


class CacheAwarePromptCompiler:
    """Plans stable prompt prefixes without invoking provider cache APIs."""

    def plan(self, sections: list[PromptSection]) -> CachePlan:
        """Return cache planning metrics for prompt sections."""

        ordered = PromptPrefixCachePlanner().order_sections(sections)
        stable = [section for section in ordered if section.stable]
        dynamic = [section for section in ordered if not section.stable]
        stable_tokens = sum(
            section.tokens or estimate_tokens(section.content) for section in stable
        )
        dynamic_tokens = sum(
            section.tokens or estimate_tokens(section.content) for section in dynamic
        )
        return CachePlan(
            stable_prefix_tokens=stable_tokens,
            dynamic_tokens=dynamic_tokens,
            cache_eligible_tokens=stable_tokens,
            cache_breaking_sections=[section.name for section in dynamic],
            recommended_order=[section.name for section in ordered],
            estimated_cache_savings_tokens=stable_tokens,
        )


class ProviderContextCacheAdapter:
    """Provider-neutral explicit-cache scaffold that never calls external APIs."""

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled
        self.created: dict[str, CachePlan] = {}

    def create(self, name: str, plan: CachePlan) -> str:
        """Record a cache plan locally if explicit caching is enabled."""

        if not self.enabled:
            return "provider_cache_disabled"
        self.created[name] = plan
        return f"local-cache-plan:{name}"


class ContextLayer(BaseModel):
    """One context layer with cache and budget metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Layer name.")
    source: str = Field(description="Layer source.")
    classification: str = Field(description="Layer data classification.")
    stability: str = Field(description="stable or dynamic.")
    cacheable: bool | str = Field(description="Cache eligibility.")
    token_budget: int = Field(ge=0, description="Layer token budget.")
    trust_level: str = Field(description="Trust label.")
    refresh_policy: str = Field(description="Refresh policy.")


class ContextLayerManager:
    """Builds provider-neutral context-layer metadata."""

    def from_config(self, config: Mapping[str, Any]) -> list[ContextLayer]:
        """Create layers from config mappings."""

        layers: list[ContextLayer] = []
        for name, data in sorted(config.items()):
            if not isinstance(data, Mapping):
                continue
            layers.append(
                ContextLayer(
                    name=name,
                    source=str(data.get("source", name)),
                    classification=str(data.get("classification", "internal")),
                    stability="stable" if data.get("cacheable") is True else "dynamic",
                    cacheable=data.get("cacheable", False),
                    token_budget=int(data.get("budget_tokens", 0)),
                    trust_level=str(data.get("trust_level", "internal")),
                    refresh_policy=str(data.get("refresh_policy", "on_demand")),
                )
            )
        return layers


class CostEntry(BaseModel):
    """Cost/tokens for one run."""

    model_config = ConfigDict(extra="forbid")

    workflow: str = Field(description="Workflow name.")
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    tool_tokens: int = Field(default=0, ge=0)
    memory_tokens: int = Field(default=0, ge=0)
    estimated_cost: float = Field(default=0.0, ge=0.0)
    estimated_latency: float = Field(default=0.0, ge=0.0)
    actual_latency: float | None = Field(default=None, ge=0.0)


class CostReport(BaseModel):
    """Aggregated cost ledger report."""

    model_config = ConfigDict(extra="forbid")

    runs: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cached_input_tokens: int = Field(ge=0)
    estimated_cost: float = Field(ge=0.0)


class CostLedger:
    """In-memory cost ledger used by CLI/report scaffolds."""

    def __init__(self) -> None:
        self.entries: list[CostEntry] = []

    def record(self, entry: CostEntry) -> None:
        """Record one entry."""

        self.entries.append(entry)

    def report(self, *, workflow: str | None = None) -> CostReport:
        """Return aggregate costs."""

        entries = [
            entry for entry in self.entries if workflow is None or entry.workflow == workflow
        ]
        return CostReport(
            runs=len(entries),
            input_tokens=sum(entry.input_tokens for entry in entries),
            output_tokens=sum(entry.output_tokens for entry in entries),
            cached_input_tokens=sum(entry.cached_input_tokens for entry in entries),
            estimated_cost=sum(entry.estimated_cost for entry in entries),
        )


class LatencyBudgetManager:
    """Checks workflow latency budgets."""

    def __init__(self, budgets: Mapping[str, int] | None = None) -> None:
        self.budgets = dict(budgets or {"ask": 20, "plan": 60, "audit": 120})

    def within_budget(self, workflow: str, seconds: float) -> bool:
        """Return whether a workflow latency estimate is acceptable."""

        return seconds <= self.budgets.get(workflow, self.budgets.get("ask", 20))


class ModelRoleRouter:
    """Selects models by role without escalating to expensive providers first."""

    def __init__(self, roles: Mapping[str, Mapping[str, str]] | None = None) -> None:
        self.roles = dict(roles or {})

    def route(self, role: str) -> dict[str, str]:
        """Return provider/model for a role."""

        default = {"provider": "mock", "model": "mock-llm"}
        selected = self.roles.get(role, self.roles.get("generate", default))
        return {
            "provider": str(selected.get("provider", "mock")),
            "model": str(selected.get("model", "mock-llm")),
        }


class ModelEscalationPolicy:
    """Deterministic model escalation policy scaffold."""

    def decide(self, *, sufficient_context: bool, high_value: bool, approval: bool) -> str:
        """Return local, retrieve_more, ask_approval, or strong_model."""

        if sufficient_context:
            return "local_or_default"
        if not high_value:
            return "retrieve_more"
        if not approval:
            return "ask_approval"
        return "strong_model"


class BatchRunPlanner:
    """Plans shared retrieval for related questions."""

    def plan(self, questions: list[str]) -> dict[str, Any]:
        """Return a deterministic batch plan."""

        return {
            "questions": len(questions),
            "shared_repo_map": True,
            "shared_retrieval": len(questions) > 1,
            "separate_outputs": True,
        }


class OfflinePrecomputer:
    """Scaffolds local artifact precomputation."""

    def artifacts(self, root: Path | str) -> list[str]:
        """Return artifacts that can be prepared offline."""

        _ = Path(root)
        return [
            "repo_map",
            "symbol_index",
            "dependency_graph_scaffold",
            "token_heatmap",
            "security_scan",
            "memory_summaries",
            "workflow_static_prefixes",
        ]


class CacheWarmer:
    """Plans stable sections for cache warming without provider calls."""

    def warm(self, workflow: str) -> dict[str, Any]:
        """Return local cache warming plan."""

        return {
            "workflow": workflow,
            "provider_calls": 0,
            "sections": ["system", "tools", "project_manifest", "repo_map", "workflow_contract"],
            "status": "planned",
        }
