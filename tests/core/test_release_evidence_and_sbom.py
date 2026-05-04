from __future__ import annotations

from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.models.context import (
    ContextItem,
    ContextPriority,
    DataClassification,
    PromptSection,
    TokenBudget,
)
from opencontext_core.models.trace import RuntimeTrace
from opencontext_core.operating_model import PromptContextSBOMBuilder, ReleaseEvidenceBuilder


def test_release_evidence_stores_hashes_not_file_contents(tmp_path: Path) -> None:
    release_root = tmp_path / "dist"
    release_root.mkdir()
    (release_root / "package.txt").write_text("release artifact", encoding="utf-8")

    evidence = ReleaseEvidenceBuilder().build(release_root)

    assert evidence.files[0].path == "package.txt"
    assert evidence.files[0].sha256 != "release artifact"
    assert evidence.files[0].size_bytes == len("release artifact")
    assert not evidence.audit.findings


def test_prompt_context_sbom_hashes_prompt_and_context_metadata_only() -> None:
    trace = _trace()

    sbom = PromptContextSBOMBuilder().build(trace, policy_metadata={"mode": "private_project"})

    assert sbom.trace_id == "trace-1"
    assert sbom.prompt_hash != "system instructions"
    assert sbom.context_pack_hash != "src/auth.py"
    assert sbom.raw_prompt_included is False
    assert sbom.memory_refs == ["mem-001"]
    assert sbom.selected_sources == ["src/auth.py", "mem-001"]


def _trace() -> RuntimeTrace:
    selected = [
        ContextItem(
            id="ctx-1",
            content="AccessResolver handles auth.",
            source="src/auth.py",
            source_type="file",
            priority=ContextPriority.P1,
            tokens=8,
            score=0.9,
            classification=DataClassification.INTERNAL,
        ),
        ContextItem(
            id="mem-001",
            content="Auth is centralized.",
            source="mem-001",
            source_type="memory",
            priority=ContextPriority.P0,
            tokens=5,
            score=1.0,
            classification=DataClassification.INTERNAL,
        ),
    ]
    return RuntimeTrace(
        run_id="run-1",
        trace_id="trace-1",
        workflow_name="review",
        input="Review auth",
        provider="mock",
        model="mock-llm",
        selected_context_items=selected,
        discarded_context_items=[],
        token_budget=TokenBudget(
            max_input_tokens=1000,
            reserve_output_tokens=200,
            available_context_tokens=800,
            sections={},
        ),
        token_estimates={"final_context_pack": 13, "prompt": 20},
        compression_strategy="none",
        prompt_sections=[
            PromptSection(name="system", content="system instructions", tokens=4),
            PromptSection(name="tool_schemas", content='{"tools":[]}', stable=True, tokens=3),
        ],
        final_answer="ok",
        created_at=datetime.now(tz=UTC),
        metadata={"security_mode": "private_project"},
    )
