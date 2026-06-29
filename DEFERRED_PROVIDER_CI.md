# Deferred Provider-CI Acceptance Gates (Option A)

Authority: SPEC `vnext-default-migration` VDM-008 + the doc-57 final-1.0 acceptance
gate set. This record documents the two 1.0 acceptance gates that are **deferred** to a
provider-CI lane under **Option A**, and the exact condition that promotes them back to
mandatory.

## Deferred gates

| Gate | Category | Why it needs a live provider |
|------|----------|------------------------------|
| `kg-retrieval-precision` | A | Requires real embeddings + an indexed runtime to compute R@5 / MRR over labeled retrieval tasks. |
| `context-token-efficiency` | A | Requires real context builds (CON vs SIN packs) to compare token use against a parity-gated baseline. |

## Decision (Option A)

- OpenContext 1.0 does **not** hard-require a live LLM/embeddings provider in CI.
- Both gates ship their runner **hooks** today:
  - `evaluation/runner.py::RecallSuite(provider=...)` accepts a `recall_provider`
    callable (`RunnerConfig.recall_provider`).
  - `evaluation/runner.py::EfficiencySuite(provider=...)` accepts an
    `efficiency_provider` callable (`RunnerConfig.efficiency_provider`).
- When no provider callable is injected, each gate reports **`NOT_MEASURED`** — never
  `FAILED` and never a fabricated `MET` (build-rule #1, HONESTY).
- Per `AcceptanceEvaluator` (`operating_model/release_gate.py`), these two gates'
  `NOT_MEASURED` status is **excluded from the `ready` denominator**
  (`DEFERRED_PROVIDER_CI_GATES`), so their deferral does **not** force `ready=False`.
  A *real* `FAILED` verdict (when a provider hook is supplied and the measurement
  fails) still blocks the release.

## How to activate them (no code change required)

Inject the provider callables and they produce a genuine `MET` / `FAILED`:

```python
from opencontext_core.evaluation.runner import RunnerConfig, build_default_runner

runner = build_default_runner(RunnerConfig(
    recall_provider=my_recall_eval,        # (root, smoke) -> RecallReport
    efficiency_provider=my_efficiency_eval, # (root, smoke) -> EfficiencyReport
))
```

## Promotion trigger (re-evaluation)

When a persistent **provider-CI lane** (credentialed embeddings + a real indexed
fixture corpus) is established, both gates **MUST** be promoted to mandatory — wired in
the provider-CI workflow and removed from `DEFERRED_PROVIDER_CI_GATES` — **before the
next minor release**. Until then they remain deferred and annotated as such in the
`release acceptance` output.
