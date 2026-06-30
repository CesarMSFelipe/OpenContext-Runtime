"""Shared registry substrate for personas, skills, and harnesses (PR-006, L6).

One base pattern (``Registry[T]`` + ``Definition`` + ``RegistryMetadata``) and one
cross-reference validator reused by all three registries, so they are coherent
governance contracts instead of three bespoke lookups.
"""

from __future__ import annotations

from opencontext_core.registries.base import (
    Definition,
    DuplicateDefinition,
    Registry,
    RegistryError,
    RegistryMetadata,
    RegistryNotFound,
    RegistrySource,
    TrustLevel,
)
from opencontext_core.registries.loader import load_defs_from_dir, load_defs_from_file
from opencontext_core.registries.validation import (
    CrossReferenceError,
    CrossRefReport,
    DanglingReference,
    ensure_cross_references,
    validate_cross_references,
)

__all__ = [
    "CrossRefReport",
    "CrossReferenceError",
    "DanglingReference",
    "Definition",
    "DuplicateDefinition",
    "Registry",
    "RegistryError",
    "RegistryMetadata",
    "RegistryNotFound",
    "RegistrySource",
    "TrustLevel",
    "ensure_cross_references",
    "load_defs_from_dir",
    "load_defs_from_file",
    "validate_cross_references",
]
