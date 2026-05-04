"""Conservative secret scanner and redactor."""

from __future__ import annotations

import hashlib
import re

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.safety.scanners import SafetyFinding

PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.DOTALL,
)
PRIVATE_KEY_MARKER_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
PRIVATE_KEY_REGEX_LITERAL_RE = re.compile(
    r"-----BEGIN \[A-Z \]\*PRIVATE KEY-----\.\*\?-----END \[A-Z \]\*PRIVATE KEY-----"
)
PRIVATE_KEY_HEADER_LINE_RE = re.compile(r"-----BEGIN .*PRIVATE KEY-----")
OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")
ANTHROPIC_KEY_RE = re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")
GITHUB_TOKEN_RE = re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")
AWS_ACCESS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
DATABASE_URL_RE = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis)://[^\s'\"<>]+",
    re.IGNORECASE,
)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")
SLACK_TOKEN_RE = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
GOOGLE_API_KEY_RE = re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")
STRIPE_KEY_RE = re.compile(r"\b(?:sk|rk)_(?:live|test)_[0-9A-Za-z]{16,}\b")
ENV_SECRET_RE = re.compile(
    r"(?mi)^([A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY|DATABASE_URL)"
    r"[A-Z0-9_]*\s*=\s*)([^\s#]+)"
)


class SecretFinding(BaseModel):
    """Secret scanner finding that never stores the raw matched value."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="Secret kind.")
    start: int = Field(ge=0, description="Start character offset.")
    end: int = Field(ge=0, description="End character offset.")
    fingerprint: str = Field(description="Short stable hash of the secret value.")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence.")
    redacted_value: str = Field(description="Redacted placeholder safe for traces.")


class SecretScanner:
    """Detects and redacts common secret patterns without modifying files."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return conservative secret findings."""

        findings: list[SafetyFinding] = []
        findings.extend(_find_all("private_key", PRIVATE_KEY_RE, text))
        findings.extend(_find_all("private_key_regex_literal", PRIVATE_KEY_REGEX_LITERAL_RE, text))
        findings.extend(_find_all("private_key_marker", PRIVATE_KEY_MARKER_RE, text))
        findings.extend(_find_all("openai_api_key", OPENAI_KEY_RE, text))
        findings.extend(_find_all("anthropic_api_key", ANTHROPIC_KEY_RE, text))
        findings.extend(_find_all("github_token", GITHUB_TOKEN_RE, text))
        findings.extend(_find_all("aws_access_key", AWS_ACCESS_KEY_RE, text))
        findings.extend(_find_all("database_url", DATABASE_URL_RE, text))
        findings.extend(_find_all("jwt_like_token", JWT_RE, text))
        findings.extend(_find_all("slack_token", SLACK_TOKEN_RE, text))
        findings.extend(_find_all("google_api_key", GOOGLE_API_KEY_RE, text))
        findings.extend(_find_all("stripe_key", STRIPE_KEY_RE, text))
        for match in ENV_SECRET_RE.finditer(text):
            if match.group(2).startswith("[REDACTED"):
                continue
            findings.append(
                SafetyFinding(
                    kind="env_secret",
                    start=match.start(2),
                    end=match.end(2),
                    value="[REDACTED]",
                    severity="warning",
                )
            )
        return sorted(findings, key=lambda finding: (finding.start, finding.end))

    def redact(self, text: str) -> str:
        """Return text with detected secret values replaced by placeholders."""

        findings = self.scan(text)
        if not findings:
            return PRIVATE_KEY_HEADER_LINE_RE.sub("[REDACTED:private_key_marker]", text)
        redacted_parts: list[str] = []
        cursor = 0
        for finding in findings:
            if finding.start < cursor:
                continue
            redacted_parts.append(text[cursor : finding.start])
            redacted_parts.append(f"[REDACTED:{finding.kind}]")
            cursor = finding.end
        redacted_parts.append(text[cursor:])
        return PRIVATE_KEY_HEADER_LINE_RE.sub(
            "[REDACTED:private_key_marker]",
            "".join(redacted_parts),
        )

    def scan_secret_findings(self, text: str) -> list[SecretFinding]:
        """Return fingerprint-only secret findings safe for traces and reports."""

        findings: list[SecretFinding] = []
        for finding in self.scan(text):
            raw_value = text[finding.start : finding.end]
            findings.append(
                SecretFinding(
                    kind=finding.kind,
                    start=finding.start,
                    end=finding.end,
                    fingerprint=_fingerprint(raw_value),
                    confidence=_confidence_for_kind(finding.kind),
                    redacted_value=f"[REDACTED:{finding.kind}]",
                )
            )
        return findings


def _find_all(kind: str, pattern: re.Pattern[str], text: str) -> list[SafetyFinding]:
    return [
        SafetyFinding(kind=kind, start=match.start(), end=match.end(), value="[REDACTED]")
        for match in pattern.finditer(text)
    ]


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _confidence_for_kind(kind: str) -> float:
    if kind == "env_secret":
        return 0.8
    if kind == "jwt_like_token":
        return 0.85
    return 0.95
