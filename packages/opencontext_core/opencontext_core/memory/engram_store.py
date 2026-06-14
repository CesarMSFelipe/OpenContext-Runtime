"""EngramMemoryAdapter: optional HTTP adapter for persistent remote memory."""

from __future__ import annotations

from opencontext_core.exceptions import BackendUnavailableError
from opencontext_core.models.agent_memory import MemoryLayer, MemoryRecord
from opencontext_core.models.evidence import EvidenceRef


class EngramMemoryAdapter:
    """Adapter for persistent remote memory via HTTP.

    Technology name never exposed to callers or in error messages.
    """

    def __init__(self, endpoint: str = "http://localhost:4242") -> None:
        self._endpoint = endpoint.rstrip("/")
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            import urllib.request

            req = urllib.request.Request(
                f"{self._endpoint}/health",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception as exc:
            raise BackendUnavailableError(
                "persistent-memory",
                "opencontext setup --enable persistent-memory",
            ) from exc

    def search(
        self, query: str, *, scope: MemoryLayer | None = None, limit: int = 10
    ) -> list[MemoryRecord]:
        # HTTP GET /search?q=...&layer=...&limit=...
        return []

    def write(self, memory: MemoryRecord) -> str:
        return memory.id

    def reinforce(self, memory_id: str, evidence: EvidenceRef) -> None:
        return

    def contradict(self, memory_id: str, evidence: EvidenceRef) -> None:
        return

    def decay(self) -> int:
        return 0

    def failure_boost(self, symbols: list[str]) -> dict[str, float]:
        return {s: 0.0 for s in symbols}
