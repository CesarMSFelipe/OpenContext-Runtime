from __future__ import annotations

from pathlib import Path

from opencontext_core.operating_model import SourceMapDetector


def test_source_map_detector_detects_marker(tmp_path: Path) -> None:
    path = tmp_path / "app.js"
    path.write_text("//# sourceMappingURL=app.js.map", encoding="utf-8")

    assert SourceMapDetector().scan_path(path)
