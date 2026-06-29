"""HarnessDefinition — first-class harness contract (PR-006, Harness Contract v1).

The branch already ships harness *behaviour* (``HarnessRunner``, phase gates in
``gates.py``, the phase→gate matrix in ``config.py``). This model names each harness
as a declarative contract (book doc 07 §4): id/type/default_mode/gates/metrics/
receipts/failure_modes. Built-ins bind the gate ids already implemented in
``gates.py``; Diagnosis/Escalation/Protocol/Consolidation/Evaluation declare their
book gate ids whose behaviour lands in PR-007.

Layer L6: imports only L0 (compat) + the L6 base.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.registries.base import RegistryMetadata

# Harness Contract v1 (doc 59 — internal contract versioning).
HARNESS_CONTRACT_VERSION = 1
HARNESS_SCHEMA_VERSION = "opencontext.harness.v1"

HarnessMode = Literal["off", "warn", "strict"]


class HarnessDefinition(BaseModel):
    """A registry-driven harness contract (book doc 07 §4)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(default=HARNESS_SCHEMA_VERSION)
    id: str = Field(description="Harness id (slug), e.g. 'mutation'. Registry key.")
    version: str = "1.0"
    type: str = Field(default="governance", description="Harness type/category.")
    description: str = ""
    default_mode: HarnessMode = Field(description="off | warn | strict (book §5).")
    required_capabilities: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    gates: list[str] = Field(default_factory=list, description="Gate ids this harness runs.")
    metrics: list[str] = Field(default_factory=list)
    receipts: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)

    metadata: RegistryMetadata = Field(default_factory=RegistryMetadata)
