"""AICXCompiler: EvidencePlan → ContextBytecode."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import TYPE_CHECKING

from opencontext_core.context.bytecode.models import (
    VERSION,
    BytecodeInstruction,
    ContextBytecode,
    ExpandMode,
    OpCode,
)
from opencontext_core.retrieval.contracts import EvidencePlan

if TYPE_CHECKING:
    from opencontext_core.compression.ccr_cache import CCRCacheBackend

_log = logging.getLogger(__name__)


def _smart_crush(content: str) -> str:
    """Compress JSON content with SmartCrusher if applicable; else return as-is."""
    stripped = content.strip()
    if not (stripped.startswith("[") or stripped.startswith("{")):
        return content
    try:
        from opencontext_core.compression.smart_crusher import compress as _sc

        return _sc(content, min_array_length=3)
    except Exception as exc:
        _log.debug("SmartCrusher skipped for AICX evidence: %s", exc)
        return content


class AICXCompiler:
    """Compiles an EvidencePlan into compact AICX bytecode.

    All text stays as dictionary references. No evidence content is inlined
    unless expand_mode=INLINE is explicitly requested.

    When ``ccr_backend`` is provided, large INLINE evidence bodies are stored
    in the CCR cache and the dictionary entry becomes ``ccr:<hash>``.  The
    decoder transparently expands these on decode.  Old decoders receive the
    token string as-is (graceful degradation — no version bump required).
    """

    def compile(
        self,
        plan: EvidencePlan,
        *,
        default_expand_mode: ExpandMode = ExpandMode.HANDLE,
        ccr_backend: CCRCacheBackend | None = None,
        ccr_threshold_chars: int = 500,
    ) -> ContextBytecode:
        dictionary: dict[str, str] = {}
        instructions: list[BytecodeInstruction] = []
        _counter = [0]

        def _short(value: str, prefix: str = "v") -> str:
            """Intern a string into the dictionary, return short key."""
            for k, v in dictionary.items():
                if v == value:
                    return k
            _counter[0] += 1
            key = f"{prefix}{_counter[0]:03d}"
            dictionary[key] = value
            return key

        request_id = str(uuid.uuid4())[:8]

        # REQ instruction
        q_key = _short(plan.request.query, "q")
        instructions.append(
            BytecodeInstruction(
                op=OpCode.REQUEST,
                args=[
                    f"id:{request_id}",
                    f"surface:{plan.request.surface.value}",
                    f"risk:{plan.request.risk_level}",
                    f"budget:{plan.request.max_tokens}",
                    f"q:{q_key}",
                ],
            )
        )

        # EVID instructions — references by default. INLINE/protected items inline
        # their content into the dictionary so the roundtrip is lossless for the
        # last-mile evidence that must survive to the LLM boundary.
        for item in plan.evidence:
            src_key = _short(item.source, "s")
            mode = ExpandMode.INLINE if item.protected else default_expand_mode
            args = [
                f"id:{item.id[:8]}",
                f"src:{src_key}",
                f"type:{item.source_type}",
                f"conf:{item.confidence:.2f}",
                f"fresh:{item.freshness.value}",
                f"tok:{item.tokens}",
                f"mode:{mode.value}",
            ]
            if mode is ExpandMode.INLINE and item.content:
                content_val = _smart_crush(item.content)
                if ccr_backend and len(content_val) >= ccr_threshold_chars:
                    from opencontext_core.compression.ccr_cache import store_original

                    ccr_hash = store_original(
                        item.content,
                        content_val,
                        content_type="evidence",
                        backend=ccr_backend,
                    )
                    content_val = f"ccr:{ccr_hash}"
                args.append(f"c:{_short(content_val, 'c')}")
            if item.protected:
                args.append("protected:1")
            instructions.append(BytecodeInstruction(op=OpCode.EVIDENCE, args=args))

        # GATE instructions
        for gate_name in _infer_gates(plan):
            instructions.append(
                BytecodeInstruction(
                    op=OpCode.GATE,
                    args=[gate_name],
                )
            )

        # OMIT instructions
        for omission in plan.omissions:
            omit_key = _short(omission, "o")
            instructions.append(
                BytecodeInstruction(
                    op=OpCode.OMIT,
                    args=[f"reason:{omit_key}"],
                )
            )

        # FALLBACK instructions
        for action in plan.fallback_actions:
            fb_key = _short(action, "f")
            instructions.append(
                BytecodeInstruction(
                    op=OpCode.FALLBACK,
                    args=[f"action:{fb_key}"],
                )
            )

        # TRUST instruction
        trust_key = _short(plan.trust_decision.reason, "t")
        instructions.append(
            BytecodeInstruction(
                op=OpCode.TRUST,
                args=[
                    f"status:{plan.trust_decision.status}",
                    f"why:{trust_key}",
                ],
            )
        )

        checksum = _compute_checksum(VERSION, dictionary, instructions)

        return ContextBytecode(
            version=VERSION,
            request_id=request_id,
            dictionary=dictionary,
            instructions=instructions,
            checksum=checksum,
        )


def _infer_gates(plan: EvidencePlan) -> list[str]:
    gates = ["provenance", "freshness", "coverage"]
    if plan.request.risk_level == "high":
        gates += ["security", "integrity"]
    return gates


def _compute_checksum(
    version: str,
    dictionary: dict[str, str],
    instructions: list[BytecodeInstruction],
) -> str:
    payload = json.dumps(
        {
            "v": version,
            "d": dictionary,
            "i": [[instr.op, instr.args] for instr in instructions],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:12]
