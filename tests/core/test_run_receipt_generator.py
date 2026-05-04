from __future__ import annotations

from opencontext_core.operating_model import RunReceiptGenerator


def test_run_receipt_generator_hashes_artifacts() -> None:
    receipt = RunReceiptGenerator().generate(
        workflow_id="review",
        policy="policy",
        context_pack="context",
        prompt="prompt",
        provider="mock",
        model="mock-llm",
        trace_id="trace",
        input_tokens=1,
        output_tokens=2,
    )

    assert receipt.policy_hash != "policy"
    assert receipt.prompt_hash != "prompt"
