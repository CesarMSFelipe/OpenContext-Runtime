from __future__ import annotations

from opencontext_core.operating_model import PromptSecretLinter


def test_prompt_secret_linter_finds_redacted_secret() -> None:
    findings = PromptSecretLinter().audit_text("key sk-abcdefghijklmnopqrstuvwxyz123456")

    assert findings
    assert all("sk-" not in finding.detail for finding in findings)
