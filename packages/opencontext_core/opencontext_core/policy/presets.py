"""Policy presets — four named, switchable governance postures (SPEC PE-3).

``balanced`` is the default (network deny, redact secrets, ask for high-risk
writes, block forbidden paths). ``restricted`` (alias ``enterprise``) and
``air_gapped`` map onto the existing :class:`~opencontext_core.config.SecurityMode`
branches already enforced by ``provider_policy``/``permissions``/``actions.policy``
so the preset reuses — rather than duplicates — those decisions (AD#3).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from opencontext_core.compat import StrEnum
from opencontext_core.config import SecurityMode

# Verb a posture assigns to a governed category before the engine finalises it.
PostureVerb = str  # one of "allow" | "ask" | "deny"


class PolicyPreset(StrEnum):
    """The four selectable policy postures (SPEC PE-3)."""

    PERMISSIVE = "permissive"
    BALANCED = "balanced"
    RESTRICTED = "restricted"
    AIR_GAPPED = "air_gapped"


# ``balanced`` is the default posture when no preset is configured (PE-3).
DEFAULT_PRESET = PolicyPreset.BALANCED

# ``enterprise`` is an accepted alias for ``restricted`` (PE-3 / AD#3).
_ALIASES = {"enterprise": PolicyPreset.RESTRICTED}


class PresetPosture(BaseModel):
    """The per-category verbs a preset assigns before final adjudication."""

    model_config = ConfigDict(extra="forbid")

    network: PostureVerb = "deny"
    external_provider: PostureVerb = "ask"
    high_risk_write: PostureVerb = "ask"
    unknown_command: PostureVerb = "ask"
    destructive_command: PostureVerb = "ask"
    redact_secrets: bool = True
    block_forbidden_paths: bool = True
    command_enforcement: bool = True
    # Highest classification that may be cached / kept (CONV.1). Anything above
    # this is denied. Ordered low→high in ``_CLASSIFICATION_ORDER``.
    cache_ceiling: str = "confidential"


PRESET_TABLE: dict[PolicyPreset, PresetPosture] = {
    PolicyPreset.PERMISSIVE: PresetPosture(
        network="ask",
        external_provider="allow",
        high_risk_write="ask",
        unknown_command="allow",
        destructive_command="ask",
        redact_secrets=True,
        block_forbidden_paths=True,
        command_enforcement=True,
        cache_ceiling="secret",
    ),
    PolicyPreset.BALANCED: PresetPosture(
        network="deny",
        external_provider="ask",
        high_risk_write="ask",
        unknown_command="ask",
        destructive_command="ask",
        redact_secrets=True,
        block_forbidden_paths=True,
        command_enforcement=True,
        cache_ceiling="confidential",
    ),
    PolicyPreset.RESTRICTED: PresetPosture(
        network="deny",
        external_provider="ask",
        high_risk_write="deny",
        unknown_command="deny",
        destructive_command="deny",
        redact_secrets=True,
        block_forbidden_paths=True,
        command_enforcement=True,
        cache_ceiling="internal",
    ),
    PolicyPreset.AIR_GAPPED: PresetPosture(
        network="deny",
        external_provider="deny",
        high_risk_write="deny",
        unknown_command="deny",
        destructive_command="deny",
        redact_secrets=True,
        block_forbidden_paths=True,
        command_enforcement=True,
        cache_ceiling="internal",
    ),
}

# Classification ordering for the cache ceiling (CONV.1). Higher index = more
# sensitive; an entry above the preset ceiling is denied.
_CLASSIFICATION_ORDER = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "secret": 3,
    "regulated": 4,
}

# Map a preset onto the existing SecurityMode where they overlap (AD#3). The new
# ``permissive``/``balanced`` postures have no stricter SecurityMode equivalent
# and resolve to the project default.
_PRESET_TO_SECURITY_MODE = {
    PolicyPreset.PERMISSIVE: SecurityMode.PRIVATE_PROJECT,
    PolicyPreset.BALANCED: SecurityMode.PRIVATE_PROJECT,
    PolicyPreset.RESTRICTED: SecurityMode.ENTERPRISE,
    PolicyPreset.AIR_GAPPED: SecurityMode.AIR_GAPPED,
}


def resolve_preset(name: str | PolicyPreset | None) -> PolicyPreset:
    """Resolve a preset name (incl. the ``enterprise`` alias) to a preset.

    Falls back to :data:`DEFAULT_PRESET` (``balanced``) for unknown/empty input.
    """
    if isinstance(name, PolicyPreset):
        return name
    if not name:
        return DEFAULT_PRESET
    key = str(name).strip().lower()
    if key in _ALIASES:
        return _ALIASES[key]
    try:
        return PolicyPreset(key)
    except ValueError:
        return DEFAULT_PRESET


def preset_from_security_mode(mode: SecurityMode) -> PolicyPreset:
    """Derive the closest preset from a configured :class:`SecurityMode`."""
    if mode is SecurityMode.AIR_GAPPED:
        return PolicyPreset.AIR_GAPPED
    if mode is SecurityMode.ENTERPRISE:
        return PolicyPreset.RESTRICTED
    return DEFAULT_PRESET


def security_mode_for_preset(preset: PolicyPreset) -> SecurityMode:
    """Return the :class:`SecurityMode` the preset reuses for enforcement (AD#3)."""
    return _PRESET_TO_SECURITY_MODE[preset]


def posture_for(preset: PolicyPreset) -> PresetPosture:
    """Return the per-category posture for a preset."""
    return PRESET_TABLE[preset]


def classification_rank(classification: str) -> int:
    """Return the sensitivity rank of a classification (unknown = most sensitive)."""
    most_sensitive = max(_CLASSIFICATION_ORDER.values())
    return _CLASSIFICATION_ORDER.get(classification.strip().lower(), most_sensitive)


def exceeds_ceiling(classification: str, ceiling: str) -> bool:
    """True when *classification* is more sensitive than the preset *ceiling*."""
    return classification_rank(classification) > classification_rank(ceiling)
