from __future__ import annotations

from opencontext_core.compat import StrEnum


class ContextMode(StrEnum):
    ASK = "ask"
    PLAN = "plan"
    ARCHITECT = "architect"
    ACT = "act"
    REVIEW = "review"
    AUDIT = "audit"
    DEBUG = "debug"
    IMPLEMENT_PACK = "implement-pack"
    VALIDATE = "validate"
    ORCHESTRATE = "orchestrate"
    ENTERPRISE = "enterprise"
    AIR_GAPPED = "air-gapped"
    CUSTOM = "custom"
