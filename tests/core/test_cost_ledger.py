from __future__ import annotations

from opencontext_core.operating_model import CostEntry, CostLedger


def test_cost_ledger_aggregates_tokens() -> None:
    ledger = CostLedger()
    ledger.record(CostEntry(workflow="ask", input_tokens=10, output_tokens=4))

    report = ledger.report()

    assert report.runs == 1
    assert report.input_tokens == 10
