"""MemoryAccessReport — per-phase read/write ledger (slice 5, CAP5.Memory).

Records which memory keys a phase touched, grouped by phase name. Pure data
structure: no IO, no conductor coupling, no enumeration of runs. Spec scenario:

- Scenario: Read access recorded — a phase reading ``spec/my-change`` must
  produce an entry ``{key: 'spec/my-change', op: 'read', phase_name: 'spec'}``.
- Multi-phase grouping — keys from different phases land under distinct
  phase buckets.
"""

from __future__ import annotations

from opencontext_core.memory.access_report import AccessEntry, MemoryAccessReport


def test_record_read_creates_entry_in_phase_group() -> None:
    """Reading 'spec/my-change' during phase 'spec' records one entry."""
    report = MemoryAccessReport()
    report.record_read("spec/my-change", phase="spec")

    entries = report.entries["spec"]
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, AccessEntry)
    assert entry.key == "spec/my-change"
    assert entry.op == "read"
    assert entry.phase_name == "spec"


def test_record_write_creates_entry_with_op_write() -> None:
    """Writing a key is recorded with op='write'."""
    report = MemoryAccessReport()
    report.record_write("decisions/run-1", phase="apply")

    entries = report.entries["apply"]
    assert len(entries) == 1
    assert entries[0].op == "write"
    assert entries[0].key == "decisions/run-1"
    assert entries[0].phase_name == "apply"


def test_multiple_phases_are_grouped_independently() -> None:
    """Triangulate: entries from spec vs apply appear as distinct phase buckets."""
    report = MemoryAccessReport()
    report.record_read("spec/foo", phase="spec")
    report.record_read("memory/working", phase="apply")
    report.record_write("receipt/run-1", phase="apply")

    assert set(report.entries.keys()) == {"spec", "apply"}
    assert [e.key for e in report.entries["spec"]] == ["spec/foo"]
    assert [e.key for e in report.entries["apply"]] == ["memory/working", "receipt/run-1"]
    assert [e.op for e in report.entries["apply"]] == ["read", "write"]


def test_entries_default_to_empty_dict() -> None:
    """Fresh report carries no phase buckets until something is recorded."""
    report = MemoryAccessReport()
    assert report.entries == {}
    assert "spec" not in report.entries


def test_access_entry_is_immutable() -> None:
    """AccessEntry is frozen — a logged access cannot be silently mutated later."""
    entry = AccessEntry(key="k", op="read", phase_name="spec")
    import dataclasses

    try:
        entry.key = "mutated"  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("AccessEntry must be frozen")
    assert entry.key == "k"
