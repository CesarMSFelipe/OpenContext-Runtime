"""Compatibility helpers for supported Python versions."""

from __future__ import annotations

from datetime import timezone
from enum import StrEnum

UTC = timezone.utc  # noqa: UP017

__all__ = ["UTC", "StrEnum"]
