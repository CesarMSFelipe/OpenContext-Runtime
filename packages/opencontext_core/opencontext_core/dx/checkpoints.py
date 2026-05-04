"""Context checkpoint scaffolding."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextCheckpoint:
    project_hash: str
    manifest_hash: str
    repo_map_hash: str
    policy_hash: str
    context_pack_hash: str
    prompt_hash: str
    trace_id: str


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
