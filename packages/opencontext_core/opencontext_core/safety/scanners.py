"""Safety scanner interfaces and shared models."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class SafetyFinding(BaseModel):
    """A conservative safety finding emitted by a scanner."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="Finding kind.")
    start: int = Field(ge=0, description="Start character offset.")
    end: int = Field(ge=0, description="End character offset.")
    value: str = Field(description="Matched sensitive value.")
    severity: str = Field(default="warning", description="Finding severity.")


class InputScanner(Protocol):
    """Interface for scanning inputs before they reach a model."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return safety findings for input text."""


class OutputScanner(Protocol):
    """Interface for scanning model outputs."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return safety findings for output text."""


class PromptInjectionDetector(Protocol):
    """Future prompt-injection detector boundary."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return prompt-injection findings."""


class PiiScanner(Protocol):
    """Interface for detecting PII content."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return PII findings."""


class DlpScanner(Protocol):
    """Interface for generic DLP scanning."""

    def scan(self, text: str) -> list[SafetyFinding]:
        """Return DLP findings."""
