from __future__ import annotations

from pathlib import Path

from opencontext_core.workflow_packs.signing import WorkflowPackSigner, WorkflowPackVerifier


def test_workflow_pack_signing_verifies_local_integrity(tmp_path: Path) -> None:
    pack = tmp_path / "review"
    pack.mkdir()
    (pack / "workflow.yaml").write_text("name: review\n", encoding="utf-8")

    signature_path = WorkflowPackSigner().write_signature(pack, key="local-secret")

    assert signature_path.exists()
    assert WorkflowPackVerifier().verify(pack, key="local-secret") is True
    assert WorkflowPackVerifier().verify(pack, key="wrong-secret") is False


def test_workflow_pack_signature_changes_when_pack_changes(tmp_path: Path) -> None:
    pack = tmp_path / "review"
    pack.mkdir()
    (pack / "workflow.yaml").write_text("name: review\n", encoding="utf-8")
    WorkflowPackSigner().write_signature(pack, key="local-secret")

    (pack / "workflow.yaml").write_text("name: review\nmode: audit\n", encoding="utf-8")

    assert WorkflowPackVerifier().verify(pack, key="local-secret") is False
