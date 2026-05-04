"""Cache interfaces and deterministic key generation."""

from __future__ import annotations

import hashlib
import json
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class CacheKey(BaseModel):
    """Deterministic cache key fields for prompt and response caches."""

    model_config = ConfigDict(extra="forbid")

    workflow_name: str = Field(description="Workflow name.")
    tenant_id: str = Field(default="default", description="Tenant scope.")
    project_id: str = Field(default="default", description="Project scope identifier.")
    project_hash: str = Field(description="Project manifest or project state hash.")
    provider: str = Field(default="mock", description="Provider identifier.")
    model_name: str = Field(description="Model name.")
    prompt_version: str = Field(description="Prompt assembly version.")
    classifications: tuple[str, ...] = Field(
        default=("internal",),
        description="Classifications represented in cached context.",
    )
    normalized_input_hash: str = Field(description="Hash of normalized user input.")
    context_hash: str = Field(description="Hash of selected context.")

    @property
    def value(self) -> str:
        """Return a stable key string."""

        payload = self.model_dump()
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class ResponseCache(Protocol):
    """Interface for exact response caches."""

    def get(self, key: CacheKey) -> str | None:
        """Return cached response content if present."""

    def set(self, key: CacheKey, value: str) -> None:
        """Store response content."""


class SemanticCache(Protocol):
    """Conservative semantic cache boundary, disabled by default."""

    def lookup(self, key: CacheKey, text: str) -> str | None:
        """Return a semantically similar cached response if safely reusable."""


def build_cache_key(
    *,
    workflow_name: str,
    tenant_id: str = "default",
    project_id: str = "default",
    project_hash: str,
    provider: str = "mock",
    model_name: str,
    prompt_version: str,
    user_input: str,
    context: str,
    classifications: tuple[str, ...] = ("internal",),
) -> CacheKey:
    """Build a deterministic cache key from runtime identity fields."""

    return CacheKey(
        workflow_name=workflow_name,
        tenant_id=tenant_id,
        project_id=project_id,
        project_hash=project_hash,
        provider=provider,
        model_name=model_name,
        prompt_version=prompt_version,
        classifications=tuple(sorted(set(classifications))),
        normalized_input_hash=_hash_text(_normalize(user_input)),
        context_hash=_hash_text(context),
    )


def cache_allowed_for_classifications(classifications: tuple[str, ...]) -> bool:
    """Fail closed for high-risk classifications by default."""

    blocked = {"secret", "regulated"}
    return not any(item in blocked for item in classifications)


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
