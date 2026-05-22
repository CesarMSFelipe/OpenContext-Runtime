"""Context checkpoint utilities."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass
class ContextCheckpoint:
    """A snapshot of context state for comparison."""

    project_hash: str
    manifest_hash: str
    repo_map_hash: str
    policy_hash: str
    context_pack_hash: str
    prompt_hash: str
    trace_id: str = ""


def fingerprint(text: str) -> str:
    """Generate a hash fingerprint of text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()
