from __future__ import annotations

from pathlib import Path

from opencontext_core.operating_model import PersistentApprovalInbox


def test_persistent_approval_inbox_round_trips_decisions(tmp_path: Path) -> None:
    inbox = PersistentApprovalInbox(tmp_path)

    created = inbox.request(kind="provider_use", reason="external provider requested")
    loaded = PersistentApprovalInbox(tmp_path).get(created.id)
    decided = PersistentApprovalInbox(tmp_path).decide(created.id, "approved")

    assert loaded.status == "pending"
    assert decided.status == "approved"
    assert decided.decided_at is not None
    assert PersistentApprovalInbox(tmp_path).list(status="approved") == [decided]


def test_persistent_approval_inbox_rejects_unknown_status(tmp_path: Path) -> None:
    inbox = PersistentApprovalInbox(tmp_path)
    created = inbox.request(kind="egress", reason="clipboard export")

    try:
        inbox.decide(created.id, "maybe")
    except ValueError as exc:
        assert "Unsupported approval status" in str(exc)
    else:
        raise AssertionError("Unsupported approval status should fail closed")
