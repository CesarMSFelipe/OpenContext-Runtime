"""Centralized sink guard and redaction helpers."""

from __future__ import annotations

from opencontext_core.safety.pii import BasicPiiScanner
from opencontext_core.safety.secrets import SecretScanner


class SinkGuard:
    """Applies conservative redaction before data reaches external sinks."""

    def __init__(self) -> None:
        self._secret_scanner = SecretScanner()
        self._pii_scanner = BasicPiiScanner()

    def redact(self, text: str) -> tuple[str, bool]:
        """Redact secrets and PII-like values from text."""

        secret_redacted = self._secret_scanner.redact(text)
        findings = self._pii_scanner.scan(secret_redacted)
        if not findings:
            return secret_redacted, secret_redacted != text
        chars = list(secret_redacted)
        for finding in reversed(findings):
            chars[finding.start : finding.end] = "[REDACTED:pii]"
        value = "".join(chars)
        return value, True
