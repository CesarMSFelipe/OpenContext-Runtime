from __future__ import annotations

from pathlib import Path

from opencontext_core.operating_model import ReleaseLeakScanner


def test_release_leak_scanner_detects_source_map(tmp_path: Path) -> None:
    (tmp_path / "app.js.map").write_text("{}", encoding="utf-8")

    report = ReleaseLeakScanner().scan(tmp_path)

    assert any(finding.kind == "source_map_file" for finding in report.findings)
