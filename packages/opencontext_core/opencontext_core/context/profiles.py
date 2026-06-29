"""The five context profiles (PR-010, OC-CONTEXT-001 §Context Profiles).

Each profile tunes four knobs over the existing engine — retrieval depth, compression
aggressiveness, memory limits, and the file-loading threshold. ``BALANCED`` reproduces
today's default behaviour byte-for-byte, so an unset profile is a no-op (design #8).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.models.context import ContextProfile

# Compression aggressiveness levels a profile may request.
CompressionLevel = str  # one of: "off" | "balanced" | "aggressive"


class ProfileSettings(BaseModel):
    """Resolved knobs for one context profile."""

    model_config = ConfigDict(extra="forbid")

    depth: int = Field(ge=0, description="Retrieval/graph-expansion depth (higher = deeper).")
    compression: CompressionLevel = Field(description="off | balanced | aggressive.")
    memory_limit: int = Field(ge=0, description="Max memory items consulted.")
    file_threshold: float = Field(
        ge=0.0, le=1.0, description="Relevance threshold below which a whole file is not loaded."
    )


# Named presets. BALANCED == current default behaviour.
PROFILES: dict[ContextProfile, ProfileSettings] = {
    ContextProfile.BALANCED: ProfileSettings(
        depth=2, compression="balanced", memory_limit=8, file_threshold=0.8
    ),
    ContextProfile.LOW_COST: ProfileSettings(
        depth=1, compression="aggressive", memory_limit=4, file_threshold=0.5
    ),
    ContextProfile.PERFORMANCE: ProfileSettings(
        depth=3, compression="off", memory_limit=8, file_threshold=0.9
    ),
    ContextProfile.ENTERPRISE: ProfileSettings(
        depth=2, compression="balanced", memory_limit=12, file_threshold=0.85
    ),
    ContextProfile.RESEARCH: ProfileSettings(
        depth=4, compression="off", memory_limit=20, file_threshold=0.95
    ),
}


def resolve_profile(profile: ContextProfile | str | None) -> ProfileSettings:
    """Resolve a :class:`ProfileSettings` for ``profile`` (unset -> BALANCED).

    An unknown/empty value resolves to ``BALANCED`` so behaviour is always defined
    and an unset profile is byte-identical to today.
    """
    if profile is None:
        return PROFILES[ContextProfile.BALANCED]
    try:
        key = ContextProfile(str(profile))
    except ValueError:
        return PROFILES[ContextProfile.BALANCED]
    return PROFILES[key]
