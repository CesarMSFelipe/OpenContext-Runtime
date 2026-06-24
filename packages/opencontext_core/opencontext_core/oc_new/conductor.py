"""OcNewConductor — drives the stateful oc-new flow."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from opencontext_core.compat import UTC
from opencontext_core.oc_new.flow import OC_NEW_FLOW
from opencontext_core.oc_new.models import (
    ChangeIdentity,
    NextAction,
    OcNewRunState,
    PhaseDefinition,
    PhaseState,
)
from opencontext_core.oc_new.store import OcNewStore


class OcNewConductor:
    def __init__(self, root: Path | str = ".") -> None:
        self.root = Path(root)
        self.store = OcNewStore(self.root)

    def start(self, task: str) -> OcNewRunState:
        identity = ChangeIdentity.from_task(task)
        phases = [PhaseState(name=phase.name) for phase in OC_NEW_FLOW]
        state = OcNewRunState(identity=identity, task=task, phases=phases)
        state = self._advance(state)
        self.store.save(state)
        return state

    def resume(self, run_id: str) -> OcNewRunState:
        state = self.store.load(run_id)
        state = self._advance(state)
        self.store.save(state)
        return state

    def mark_done(
        self,
        run_id: str,
        phase_name: str,
        *,
        status: str = "passed",
        artifact_paths: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> OcNewRunState:
        state = self.store.load(run_id)
        phase = state.phase(phase_name)  # type: ignore[arg-type]
        updated = phase.model_copy(
            update={
                "status": status,
                "completed_at": datetime.now(tz=UTC),
                "artifact_paths": (
                    artifact_paths if artifact_paths is not None else phase.artifact_paths
                ),
                "warnings": warnings if warnings is not None else phase.warnings,
            }
        )
        state = self._replace_phase(state, updated)
        state = self._advance(state)
        self.store.save(state)
        return state

    def _advance(self, state: OcNewRunState) -> OcNewRunState:
        for phase_def in OC_NEW_FLOW:
            phase = state.phase(phase_def.name)
            if phase.status in {"passed", "warning", "skipped"}:
                continue

            missing = self._missing_artifacts(state, phase_def)
            if missing:
                return state.model_copy(
                    update={
                        "current_phase": phase_def.name,
                        "blocked_reason": f"missing artifacts: {', '.join(missing)}",
                        "next_action": NextAction(
                            kind="blocked",
                            phase=phase_def.name,
                            persona=phase_def.persona,
                            instruction=(
                                f"Cannot run {phase_def.name}; missing: {', '.join(missing)}"
                            ),
                        ),
                        "updated_at": datetime.now(tz=UTC),
                    }
                )

            if phase_def.name == "approval":
                return state.model_copy(
                    update={
                        "current_phase": "approval",
                        "blocked_reason": None,
                        "next_action": NextAction(
                            kind="request_approval",
                            phase="approval",
                            persona=None,
                            instruction=(
                                "Show spec, design and tasks to the user. "
                                "Create approval.json before apply."
                            ),
                            expected_artifacts=["approval.json"],
                        ),
                        "updated_at": datetime.now(tz=UTC),
                    }
                )

            return state.model_copy(
                update={
                    "current_phase": phase_def.name,
                    "blocked_reason": None,
                    "next_action": NextAction(
                        kind="spawn_subagent",
                        phase=phase_def.name,
                        persona=phase_def.persona,
                        instruction=(
                            f"Run {phase_def.skill} as {phase_def.persona}. "
                            f"Use memory key {state.identity.memory_key}. "
                            f"Produce: {', '.join(phase_def.expected_artifacts)}."
                        ),
                        required_tools=phase_def.required_tools,
                        expected_artifacts=phase_def.expected_artifacts,
                    ),
                    "updated_at": datetime.now(tz=UTC),
                }
            )

        return state.model_copy(
            update={
                "current_phase": None,
                "blocked_reason": None,
                "next_action": NextAction(kind="done", instruction="oc-new completed."),
                "updated_at": datetime.now(tz=UTC),
            }
        )

    def _replace_phase(self, state: OcNewRunState, updated: PhaseState) -> OcNewRunState:
        return state.model_copy(
            update={
                "phases": [
                    updated if p.name == updated.name else p
                    for p in state.phases
                ],
                "updated_at": datetime.now(tz=UTC),
            }
        )

    def _missing_artifacts(self, state: OcNewRunState, phase_def: PhaseDefinition) -> list[str]:
        run_dir = self.root / ".opencontext" / "runs" / state.identity.run_id
        spec_dir = self.root / "openspec" / "changes" / state.identity.change_id
        missing: list[str] = []
        for artifact in phase_def.required_artifacts:
            if not (run_dir / artifact).exists() and not (spec_dir / artifact).exists():
                missing.append(artifact)
        return missing
