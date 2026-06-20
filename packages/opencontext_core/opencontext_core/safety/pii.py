"""Basic PII and DLP scanner implementation."""

from __future__ import annotations

import re

from opencontext_core.safety.scanners import SafetyFinding

_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b")
_CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def _luhn_ok(digits: str) -> bool:
    """Luhn checksum gate so a 13-19 digit run is only flagged as a card number
    when it actually validates — long build numbers / order ids are not cards."""
    nums = [int(c) for c in digits if c.isdigit()]
    if not 13 <= len(nums) <= 19:
        return False
    total = 0
    for i, digit in enumerate(reversed(nums)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


class BasicPiiScanner:
    """Conservative PII scanner used for prompt and output checks."""

    def scan(self, text: str) -> list[SafetyFinding]:
        findings: list[SafetyFinding] = []
        findings.extend(_find("email", _EMAIL_RE, text))
        findings.extend(_find("phone", _PHONE_RE, text))
        findings.extend(
            f for f in _find("credit_card_like", _CC_RE, text) if _luhn_ok(text[f.start : f.end])
        )
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
