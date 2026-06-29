"""Rollback evidence — event + receipt + report artifact (PR-002, RBK-02, L2).

When a mutation is rolled back to its checkpoint (doc 24 §13), this module emits
the full evidence trail: a ``rollback.started`` and ``rollback.completed``
:class:`RunEvent`, a :class:`RollbackReceipt`, and a ``rollback-report`` artifact
referencing the restored checkpoint. The reversible restore itself is performed
by :class:`opencontext_core.harness.checkpoint.Checkpoint` (RBK-01 unchanged).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opencontext_core.models.artifact import ArtifactWriteRequest
from opencontext_core.models.receipt import RollbackReceipt
from opencontext_core.models.trace import RunEvent

# doc 59 §Event hierarchy: rollback events belong to the ``runtime`` family.
_FAMILY = "runtime"


def rollback(
    checkpoint: Any,
    *,
    run_dir: Path | str,
    reason: str,
    session_id: str = "",
    run_id: str = "",
    artifact_store: Any = None,
    receipt_store: Any = None,
    events: list[RunEvent] | None = None,
    restore: bool = True,
) -> RollbackReceipt:
    """Restore *checkpoint* (optionally) and emit rollback evidence.

    Args:
        checkpoint: reversible :class:`~...checkpoint.Checkpoint` to restore.
        run_dir: durable run root the report/receipt are written under.
        reason: why the rollback happened (gate failure, error, rejection).
        artifact_store / receipt_store: durable stores; when ``None`` the
            corresponding evidence is skipped (the events are always produced).
        events: ledger to append the two rollback events to (created if absent).
        restore: when ``False`` the files are assumed already restored (the
            ApplyPhase inline path) and only evidence is emitted.

    Returns the written :class:`RollbackReceipt`.
    """
    events = events if events is not None else []
    run_dir = Path(run_dir)
    checkpoint_id = getattr(checkpoint, "id", "")
    restored_files = [str(p) for p in getattr(checkpoint, "paths", [])]

    events.append(
        RunEvent(
            index=len(events),
            phase="apply",
            action="rollback.started",
            inputs_summary=reason,
            status="started",
            observation=f"restoring checkpoint {checkpoint_id}",
            metadata={"family": _FAMILY, "checkpoint_id": checkpoint_id},
        )
    )

    if restore:
        checkpoint.restore()

    report_artifact_id: str | None = None
    if artifact_store is not None:
        report = {
            "checkpoint_id": checkpoint_id,
            "reason": reason,
            "restored_files": restored_files,
        }
        ref = artifact_store.write(
            ArtifactWriteRequest(
                run_id=run_id,
                session_id=session_id,
                kind="rollback-report",
                content=json.dumps(report, indent=2),
                media_type="application/json",
                produced_by="rollback",
                source="generated",
                metadata={"checkpoint_id": checkpoint_id},
            )
        )
        report_artifact_id = ref.artifact_id

    receipt = RollbackReceipt(
        run_id=run_id or None,
        session_id=session_id,
        checkpoint_id=checkpoint_id,
        restored_files=restored_files,
        reason=reason,
        report_artifact_id=report_artifact_id,
    )
    if receipt_store is not None:
        receipt_store.write(receipt)

    events.append(
        RunEvent(
            index=len(events),
            phase="apply",
            action="rollback.completed",
            inputs_summary=reason,
            status="completed",
            observation=f"restored {len(restored_files)} file(s)",
            metadata={
                "family": _FAMILY,
                "checkpoint_id": checkpoint_id,
                "receipt_id": receipt.receipt_id,
            },
        )
    )
    return receipt
