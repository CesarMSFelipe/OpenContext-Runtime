from __future__ import annotations

from opencontext_core.operating_model import ToolChainAnalyzer


def test_tool_chain_analyzer_blocks_risky_sequence() -> None:
    report = ToolChainAnalyzer().analyze(["read_secret", "external_network"])

    assert report.passed is False
    assert report.risks == ["read_secret->external_network"]
