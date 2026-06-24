"""Tests for OcNewArchiveGate."""
from __future__ import annotations

import pytest

from opencontext_core.oc_new.archive_gate import OcNewArchiveGate


def test_gate_passes_when_all_present(tmp_path):
    gate = OcNewArchiveGate()
    for name in gate.REQUIRED:
        (tmp_path / name).write_text("{}", encoding="utf-8")
    missing = gate.validate(tmp_path)
    assert missing == []


def test_gate_reports_missing(tmp_path):
    gate = OcNewArchiveGate()
    missing = gate.validate(tmp_path)
    assert set(missing) == set(gate.REQUIRED)


def test_gate_assert_raises_when_missing(tmp_path):
    gate = OcNewArchiveGate()
    with pytest.raises(RuntimeError, match="Cannot archive"):
        gate.assert_can_archive(tmp_path)


def test_gate_assert_passes_when_all_present(tmp_path):
    gate = OcNewArchiveGate()
    for name in gate.REQUIRED:
        (tmp_path / name).write_text("{}", encoding="utf-8")
    gate.assert_can_archive(tmp_path)  # must not raise
