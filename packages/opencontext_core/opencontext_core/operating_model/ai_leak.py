"""AI leak security and prompt/config/release scanning scaffolds."""

from __future__ import annotations

import base64
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from opencontext_core.safety.prompt_injection import PromptInjectionScanner
from opencontext_core.safety.redaction import SinkGuard
from opencontext_core.safety.secrets import SecretScanner

SOURCE_MAP_RE = re.compile(r"sourceMappingURL=|\.map(?:\s|$)", re.IGNORECASE)
EXTERNAL_URL_RE = re.compile(r"https?://[^\s)>\"]+")
BASE64ISH_RE = re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")
CONTROL_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069]")
AI_CONFIG_DIRS = {".claude", ".cursor", ".continue", ".opencontext", ".codex"}
RELEASE_RISK_NAMES = {".env", ".env.local", ".env.production", "opencontext.trace.json"}


class LeakFinding(BaseModel):
    """Fingerprint-only leak or exfiltration finding."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="Finding kind.")
    path: str | None = Field(default=None, description="Optional file path.")
    detail: str = Field(description="Redacted detail.")
    severity: str = Field(default="warning", description="Finding severity.")


class ReleaseAuditReport(BaseModel):
    """Release artifact audit result."""

    model_config = ConfigDict(extra="forbid")

    root: str = Field(description="Audited root.")
    findings: list[LeakFinding] = Field(description="Leak findings.")
    blocked: bool = Field(description="Whether the release gate should block.")


class PromptContract(BaseModel):
    """Public-safe contract metadata for a prompt template."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Prompt contract id.")
    purpose: str = Field(description="Prompt purpose.")
    public_safe: bool = Field(default=True, description="Whether the prompt can be public.")
    allowed_sources: list[str] = Field(default_factory=list, description="Allowed source types.")
    forbidden_content: list[str] = Field(
        default_factory=lambda: ["secrets", "raw_credentials", "private_keys"],
        description="Content that must not appear in the prompt.",
    )


class PromptSecretLinter:
    """Lints prompt text for secrets and public-safety violations."""

    def audit_text(self, text: str, *, path: str | None = None) -> list[LeakFinding]:
        """Return redacted prompt findings."""

        findings = [
            LeakFinding(
                kind=finding.kind,
                path=path,
                detail=finding.redacted_value,
                severity="error",
            )
            for finding in SecretScanner().scan_secret_findings(text)
        ]
        if "BEGIN " in text and "PRIVATE KEY" in text:
            findings.append(
                LeakFinding(
                    kind="private_key_marker",
                    path=path,
                    detail="[REDACTED:private_key_marker]",
                    severity="error",
                )
            )
        return findings


class PromptConfigSanitizer:
    """Sanitizes prompt/config structures before export or trace persistence."""

    def sanitize(self, value: Any) -> Any:
        """Return a redacted copy of nested prompt/config data."""

        guard = SinkGuard()
        if isinstance(value, Mapping):
            return {str(key): self.sanitize(child) for key, child in sorted(value.items())}
        if isinstance(value, list | tuple):
            return [self.sanitize(child) for child in value]
        if isinstance(value, str):
            return guard.redact(value)[0]
        return value


class PublicSafePromptExporter:
    """Exports redacted prompts under the assumption that prompts can leak."""

    def export(self, text: str, contract: PromptContract | None = None) -> str:
        """Return a public-safe prompt string."""

        redacted = SinkGuard().redact(text)[0]
        if contract and not contract.public_safe:
            return "[PUBLIC_EXPORT_BLOCKED:prompt_contract_not_public_safe]"
        return redacted


class SourceMapDetector:
    """Detects source maps and sourceMappingURL markers."""

    def scan_path(self, path: Path) -> list[LeakFinding]:
        """Scan one path for source-map exposure."""

        findings: list[LeakFinding] = []
        if path.suffix == ".map":
            findings.append(
                LeakFinding(kind="source_map_file", path=str(path), detail="source map artifact")
            )
        if path.is_file():
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                sample = handle.read(200_000)
            if SOURCE_MAP_RE.search(sample):
                findings.append(
                    LeakFinding(
                        kind="source_map_reference",
                        path=str(path),
                        detail="sourceMappingURL marker",
                    )
                )
        return findings


class AIConfigLeakScanner:
    """Scans AI configuration directories for secrets or risky raw artifacts."""

    def scan(self, root: Path | str) -> list[LeakFinding]:
        """Scan AI config files under a root."""

        base = Path(root)
        findings: list[LeakFinding] = []
        for path in _iter_files(base):
            if not any(part in AI_CONFIG_DIRS for part in path.parts):
                continue
            text = _read_sample(path)
            findings.extend(PromptSecretLinter().audit_text(text, path=str(path)))
            if "raw_context" in text or "store_raw_context: true" in text:
                findings.append(
                    LeakFinding(kind="raw_context_config", path=str(path), detail="raw context")
                )
        return findings


class ReleaseLeakScanner:
    """Audits release artifacts for source maps, secrets, raw traces, and AI configs."""

    def scan(self, root: Path | str) -> ReleaseAuditReport:
        """Return a local release audit report."""

        base = Path(root)
        findings: list[LeakFinding] = []
        source_map_detector = SourceMapDetector()
        for path in _iter_files(base):
            findings.extend(source_map_detector.scan_path(path))
            if path.name in RELEASE_RISK_NAMES or path.name.startswith(".env."):
                findings.append(
                    LeakFinding(kind="release_risk_file", path=str(path), detail=path.name)
                )
            text = _read_sample(path)
            findings.extend(PromptSecretLinter().audit_text(text, path=str(path)))
            if "selected_context_items" in text and "final_answer" in text:
                findings.append(
                    LeakFinding(kind="raw_trace_candidate", path=str(path), detail="trace")
                )
        findings.extend(AIConfigLeakScanner().scan(base))
        return ReleaseAuditReport(
            root=str(base),
            findings=findings,
            blocked=any(finding.severity == "error" for finding in findings),
        )


class PackageArtifactAuditor:
    """Thin release-audit facade for package/dist directories."""

    def audit(self, dist: Path | str) -> ReleaseAuditReport:
        """Audit a package artifact directory."""

        return ReleaseLeakScanner().scan(dist)


class UnicodeObfuscationScanner:
    """Detects control characters commonly used for prompt obfuscation."""

    def scan(self, text: str) -> list[LeakFinding]:
        """Return unicode obfuscation findings."""

        if CONTROL_RE.search(text):
            return [LeakFinding(kind="unicode_obfuscation", detail="zero-width/bidi control")]
        return []


class EncodedPayloadDetector:
    """Detects suspicious encoded payload-like spans in untrusted text."""

    def scan(self, text: str) -> list[LeakFinding]:
        """Return encoded payload findings."""

        findings: list[LeakFinding] = []
        for match in BASE64ISH_RE.finditer(text):
            value = match.group(0)
            try:
                decoded = base64.b64decode(value + "==", validate=False)
            except Exception:
                continue
            if len(decoded) >= 24:
                findings.append(
                    LeakFinding(kind="encoded_payload", detail="[REDACTED:encoded_payload]")
                )
        return findings


class IndirectPromptInjectionFirewall:
    """Keeps untrusted source content from becoming instructions."""

    def scan(self, text: str, *, trusted: bool = False) -> list[LeakFinding]:
        """Scan untrusted data for prompt-injection instructions."""

        findings: list[LeakFinding] = []
        if trusted:
            return findings
        findings.extend(
            LeakFinding(kind=finding.kind, detail=finding.value, severity=finding.severity)
            for finding in PromptInjectionScanner().scan(text)
        )
        findings.extend(UnicodeObfuscationScanner().scan(text))
        findings.extend(EncodedPayloadDetector().scan(text))
        return findings


class OutputExfiltrationScanner:
    """Scans outbound output before CLI/API/trace/file/clipboard sinks."""

    def scan(self, text: str) -> list[LeakFinding]:
        """Return exfiltration findings without exposing raw secrets."""

        findings = PromptSecretLinter().audit_text(text)
        for match in EXTERNAL_URL_RE.finditer(text):
            findings.append(
                LeakFinding(kind="external_url", detail=match.group(0), severity="warning")
            )
        return findings


class EgressDecision(BaseModel):
    """Decision for one egress attempt."""

    model_config = ConfigDict(extra="forbid")

    channel: str = Field(description="Egress channel.")
    decision: str = Field(description="allow, ask, or deny.")
    reason: str = Field(description="Policy reason.")

    @property
    def allowed(self) -> bool:
        """Return whether the decision permits immediate egress."""

        return self.decision == "allow"


class EgressPolicyEngine:
    """Evaluates egress policy values from config."""

    def __init__(self, policy: Mapping[str, str] | None = None) -> None:
        self.policy = {
            "network": "deny",
            "external_urls": "ask",
            "webhooks": "deny",
            "clipboard": "allow_redacted",
            "file_export": "allow_redacted",
            "tool_output_forwarding": "deny",
            **dict(policy or {}),
        }

    def evaluate(self, channel: str, *, redacted: bool = True) -> EgressDecision:
        """Evaluate one egress channel."""

        raw = self.policy.get(channel, "deny")
        if raw == "allow_redacted":
            return EgressDecision(
                channel=channel,
                decision="allow" if redacted else "deny",
                reason="redacted_output_required",
            )
        if raw in {"allow", "ask", "deny"}:
            return EgressDecision(channel=channel, decision=raw, reason=f"policy:{raw}")
        return EgressDecision(channel=channel, decision="deny", reason="unknown_policy_value")


class SourceTrustBoundary(BaseModel):
    """Trust metadata for a source entering context."""

    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(description="Source type.")
    trust_level: str = Field(description="trusted, internal, or untrusted.")
    tainted: bool = Field(description="Whether source is tainted.")
    allowed_actions: list[str] = Field(description="Actions this source may influence.")


class SourceTrustBoundaryMapper:
    """Maps source types to trust boundaries."""

    def map_source(self, source_type: str) -> SourceTrustBoundary:
        """Return conservative trust metadata for a source type."""

        trusted = source_type in {"policy", "system", "workflow_contract"}
        internal = source_type in {"repo_map", "memory", "file"}
        return SourceTrustBoundary(
            source_type=source_type,
            trust_level="trusted" if trusted else "internal" if internal else "untrusted",
            tainted=not trusted,
            allowed_actions=[] if not trusted else ["policy_summary"],
        )


class TaintedContext(BaseModel):
    """Taint metadata for one context payload."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(description="Source identifier.")
    content: str = Field(description="Redacted content.")
    tainted: bool = Field(description="Whether content is untrusted.")
    trust_level: str = Field(description="Trust boundary label.")


class ContextTaintTracker:
    """Tracks whether context may be treated as instructions."""

    def mark(self, source_id: str, content: str, *, source_type: str) -> TaintedContext:
        """Mark context with trust metadata."""

        boundary = SourceTrustBoundaryMapper().map_source(source_type)
        return TaintedContext(
            source_id=source_id,
            content=SinkGuard().redact(content)[0],
            tainted=boundary.tainted,
            trust_level=boundary.trust_level,
        )

    def can_promote_to_instruction(self, context: TaintedContext) -> bool:
        """Return whether content can be promoted to trusted instructions."""

        return not context.tainted and context.trust_level == "trusted"


def _iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    ignored_parts = {".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache"}
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not ignored_parts.intersection(path.parts)
    )


def _read_sample(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return handle.read(200_000)
