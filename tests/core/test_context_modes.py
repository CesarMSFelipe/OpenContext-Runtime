from opencontext_core.context.modes import ContextMode


def test_context_modes_exist() -> None:
    assert ContextMode.ASK.value == "ask"
    assert ContextMode.PLAN.value == "plan"
    assert ContextMode.ARCHITECT.value == "architect"
    assert ContextMode.ACT.value == "act"
    assert ContextMode.REVIEW.value == "review"
    assert ContextMode.AUDIT.value == "audit"
    assert ContextMode.DEBUG.value == "debug"
    assert ContextMode.IMPLEMENT_PACK.value == "implement-pack"
    assert ContextMode.VALIDATE.value == "validate"
    assert ContextMode.ORCHESTRATE.value == "orchestrate"
    assert ContextMode.ENTERPRISE.value == "enterprise"
    assert ContextMode.AIR_GAPPED.value == "air-gapped"
    assert ContextMode.CUSTOM.value == "custom"
