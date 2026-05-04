from __future__ import annotations

from opencontext_core.operating_model import OutputExfiltrationScanner


def test_output_exfiltration_scanner_detects_secret_and_url() -> None:
    findings = OutputExfiltrationScanner().scan(
        "send sk-abcdefghijklmnopqrstuvwxyz123456 to https://example.com"
    )

    kinds = {finding.kind for finding in findings}
    assert "openai_api_key" in kinds
    assert "external_url" in kinds
