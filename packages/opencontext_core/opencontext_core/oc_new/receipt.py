"""OcNewReceipt — writes the final run receipt when archiving."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.oc_new.models import OcNewRunState


def write_receipt(state: OcNewRunState, run_dir: Path) -> Path:
    """Write receipt.json into run_dir and append to .opencontext/receipts/receipts.jsonl."""
    receipt = {
        "schema_version": "opencontext.oc_new_receipt.v1",
        "run_id": state.identity.run_id,
        "change_id": state.identity.change_id,
        "trace_id": state.identity.trace_id,
        "memory_key": state.identity.memory_key,
        "task": state.task,
        "completed_phases": state.completed_phases(),
        "archived_at": datetime.now(tz=UTC).isoformat(),
    }

    receipt_path = run_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Append to global receipts ledger
    global_receipts = run_dir.parent.parent / "receipts" / "receipts.jsonl"
    global_receipts.parent.mkdir(parents=True, exist_ok=True)
    with global_receipts.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt) + "\n")

    return receipt_path
