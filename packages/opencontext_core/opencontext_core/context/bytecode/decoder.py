"""AICXDecoder: ContextBytecode → EvidencePlan (roundtrip)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from opencontext_core.context.bytecode.models import ContextBytecode, ExpandMode, OpCode
from opencontext_core.retrieval.contracts import (
    EvidenceItem,
    EvidencePlan,
    EvidenceRequest,
    FreshnessStatus,
    RetrievalSurface,
    TrustDecision,
    evidence_trace_id,
)

if TYPE_CHECKING:
    from opencontext_core.compression.ccr_cache import CCRCacheBackend


class AICXDecoder:
    """Reconstructs an EvidencePlan from a ContextBytecode.

    Content fields that were not inlined (mode=handle/if_needed) are
    restored as empty strings — the caller must re-fetch content if needed.
    This is intentional: the whole point is lazy expansion.

    Dictionary values prefixed ``ccr:<hash>`` are fetched from the CCR cache
    when a ``ccr_backend`` is supplied; otherwise the token string is returned
    as-is (compatible with old decoders that predate CCR support).
    """

    def __init__(self, *, ccr_backend: CCRCacheBackend | None = None) -> None:
        self._ccr_backend = ccr_backend

    def decode(self, bc: ContextBytecode) -> EvidencePlan:
        req_args = _parse_instr(bc, OpCode.REQUEST)
        request = EvidenceRequest(
            query=bc.get(req_args.get("q", "")),
            root=Path("."),
            surface=RetrievalSurface(req_args.get("surface", "runtime")),
            max_tokens=int(req_args.get("budget", "16000")),
            risk_level=req_args.get("risk", "normal"),
        )

        evidence: list[EvidenceItem] = []
        from opencontext_core.models.context import DataClassification

        for instr in bc.instructions:
            if instr.op != OpCode.EVIDENCE:
                continue
            a = _args_dict(instr.args)
            mode = ExpandMode(a.get("mode", "handle"))
            # INLINE/protected items carry their content in the dictionary (key "c");
            # reference-only items decode to "" (resolved lazily if ever needed).
            raw = bc.get(a["c"]) if "c" in a else ""
            content = self._expand_ccr(raw)
            evidence.append(
                EvidenceItem(
                    id=a.get("id", ""),
                    content=content,
                    source=bc.get(a.get("src", "")),
                    source_type=a.get("type", "file"),
                    provenance={"aicx_decoded": True, "expand_mode": mode.value},
                    confidence=float(a.get("conf", "0.5")),
                    freshness=FreshnessStatus(a.get("fresh", "unknown")),
                    surface=request.surface,
                    tokens=int(a.get("tok", "0")),
                    protected=a.get("protected", "0") == "1",
                    classification=DataClassification.INTERNAL,
                )
            )

        trust_args = _parse_instr(bc, OpCode.TRUST)
        trust = TrustDecision(
            status=trust_args.get("status", "unknown"),
            reason=bc.get(trust_args.get("why", "")),
        )

        omissions = [
            bc.get(v)
            for instr in bc.instructions
            if instr.op == OpCode.OMIT
            for v in [_args_dict(instr.args).get("reason", "")]
            if v
        ]

        fallbacks = [
            bc.get(v)
            for instr in bc.instructions
            if instr.op == OpCode.FALLBACK
            for v in [_args_dict(instr.args).get("action", "")]
            if v
        ]

        return EvidencePlan(
            request=request,
            evidence=evidence,
            fallback_actions=fallbacks,
            trust_decision=trust,
            trace_id=evidence_trace_id(request, [e.id for e in evidence]),
            omissions=omissions,
            source_surfaces=list({e.surface for e in evidence}),
        )

    def _expand_ccr(self, value: str) -> str:
        """Resolve a CCR token to the original content, or return as-is."""
        if not value.startswith("ccr:"):
            return value
        if self._ccr_backend is None:
            return value  # no backend — return token (graceful degradation)
        from opencontext_core.compression.ccr_cache import retrieve_original

        content_hash = value[4:]
        recovered = retrieve_original(content_hash, backend=self._ccr_backend)
        return recovered if recovered is not None else value


def _parse_instr(bc: ContextBytecode, op: str) -> dict[str, str]:
    for instr in bc.instructions:
        if instr.op == op:
            return _args_dict(instr.args)
    return {}


def _args_dict(args: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for arg in args:
        if ":" in arg:
            k, _, v = arg.partition(":")
            result[k] = v
    return result
