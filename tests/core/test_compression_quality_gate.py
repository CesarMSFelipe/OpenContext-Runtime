from __future__ import annotations

from opencontext_core.memory_usability import CompressionQualityGate


def test_compression_quality_preserves_symbols_numbers_and_sources() -> None:
    text = "AccessResolver in src/auth.py returned 403. REF: src/auth.py:12"

    report = CompressionQualityGate().evaluate(text, text, protected_spans=["AccessResolver"])

    assert report.symbols_preserved is True
    assert report.numbers_preserved is True
    assert report.source_refs_preserved is True
    assert report.quality_risk == "low"
