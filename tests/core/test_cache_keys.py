from __future__ import annotations

from opencontext_core.cache import ExactPromptCache, build_cache_key


def test_deterministic_cache_key_and_exact_hit_miss() -> None:
    key_a = build_cache_key(
        workflow_name="code_assistant",
        project_hash="project",
        model_name="mock-llm",
        prompt_version="v1",
        user_input="  Where Is Auth? ",
        context="ctx",
    )
    key_b = build_cache_key(
        workflow_name="code_assistant",
        project_hash="project",
        model_name="mock-llm",
        prompt_version="v1",
        user_input="where is auth?",
        context="ctx",
    )
    isolated = key_a.model_copy(update={"workflow_name": "other"})
    cache = ExactPromptCache()

    assert key_a.value == key_b.value
    assert cache.get(key_a) is None
    cache.set(key_a, "answer")
    assert cache.get(key_b) == "answer"
    assert cache.get(isolated) is None


def test_exact_cache_redacts_sensitive_values() -> None:
    key = build_cache_key(
        workflow_name="code_assistant",
        project_hash="project",
        model_name="mock-llm",
        prompt_version="v1",
        user_input="question",
        context="ctx",
    )
    cache = ExactPromptCache()
    cache.set(key, "Contact admin@example.com with sk-abcdefghijklmnopqrstuvwxyz123456")
    value = cache.get(key)
    assert value is not None
    assert "admin@example.com" not in value
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in value


def test_exact_cache_skips_secret_classifications() -> None:
    key = build_cache_key(
        workflow_name="code_assistant",
        project_hash="project",
        model_name="mock-llm",
        prompt_version="v1",
        user_input="question",
        context="ctx",
        classifications=("secret",),
    )
    cache = ExactPromptCache()
    cache.set(key, "redacted answer")

    assert cache.get(key) is None
