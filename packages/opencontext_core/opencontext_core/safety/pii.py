"""Basic PII and DLP scanner implementation."""

from __future__ import annotations

import re

from opencontext_core.safety.scanners import SafetyFinding

_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b")
_CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


class BasicPiiScanner:
    """Conservative PII scanner used for prompt and output checks."""

    def scan(self, text: str) -> list[SafetyFinding]:
        findings: list[SafetyFinding] = []
        findings.extend(_find("email", _EMAIL_RE, text))
        findings.extend(_find("phone", _PHONE_RE, text))
        findings.extend(_find("credit_card_like", _CC_RE, text))
        return sorted(findings, key=lambda item: (item.start, item.end))


def _find(kind: str, pattern: re.Pattern[str], text: str) -> list[SafetyFinding]:
    results: list[SafetyFinding] = []
    for match in pattern.finditer(text):
        results.append(
            SafetyFinding(
                kind=kind,
                start=match.start(),
                end=match.end(),
                value="[REDACTED]",
                severity="warning",
            )
        )
    return results
