"""Local trace persistence."""

from __future__ import annotations

from pathlib import Path

from opencontext_core.errors import MemoryStoreError
from opencontext_core.models.trace import RuntimeTrace


class LocalTraceLogger:
    """Persists runtime traces under a local directory."""

    def __init__(self, base_path: Path | str = ".storage/opencontext/traces") -> None:
        self.base_path = Path(base_path)

    def persist(self, trace: RuntimeTrace) -> Path:
        """Persist a trace as JSON and return its path."""

        self.base_path.mkdir(parents=True, exist_ok=True)
        path = self.base_path / f"{trace.run_id}.json"
        path.write_text(trace.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, trace_id: str) -> RuntimeTrace:
        """Load one trace by identifier."""

        path = self.base_path / f"{trace_id}.json"
        if not path.exists():
            raise MemoryStoreError(f"Trace not found: {trace_id}")
        return RuntimeTrace.model_validate_json(path.read_text(encoding="utf-8"))

    def latest(self) -> RuntimeTrace:
        """Load the most recently modified trace."""

        if not self.base_path.exists():
            raise MemoryStoreError(f"No trace directory found at {self.base_path}")
        traces = sorted(self.base_path.glob("*.json"), key=lambda path: path.stat().st_mtime)
        if not traces:
            raise MemoryStoreError(f"No traces found under {self.base_path}")
        return RuntimeTrace.model_validate_json(traces[-1].read_text(encoding="utf-8"))
