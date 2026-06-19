# Project State

Current status and actionable items for OpenContext Runtime.

---

## CI Status

All four gates verified at the CI scope (`ruff check .`, `ruff format --check .`,
`mypy packages/opencontext_core`, `pytest`).

| Check | Status | Details |
|-------|--------|---------|
| pytest | ✅ Pass | 1699 pass, 6 skip |
| ruff | ✅ Pass | whole repo (`ruff check .`) |
| mypy | ✅ Pass | `packages/opencontext_core` — 297 files (navigable prompts return `Any`; `str()`/`bool()` cast at typed call sites) |
| ruff format | ✅ Pass | whole repo |

### Blocker — resolved

`docs/` contained ARCHITECTURAL_REVIEW.md with two forbidden external product names; the file was deleted. The remaining trip was STATE.md itself naming those products in plaintext — reworded to generic references. The guard scans all `docs/**/*.md`, so internal planning docs must avoid the forbidden names (they are base64-encoded in the test on purpose).

---

## Navigable Prompts & Interactive UX — ✅ Done

Every interactive prompt now routes through one helper module,
`opencontext_core/prompts.py` (arrow-key `select`, space-toggle `checkbox`,
navigable `confirm`, plus `text`/`secret`/`pause`). No numbered menus, no typed
`(y/n)`. Degradation is explicit: InquirerPy+TTY → Rich text → non-TTY returns
the default (never hangs).

Converted from numbered menus / `Confirm.ask` / `Prompt.ask` / `input()`:
`menu_cmd.py` (main menu, backups, restore, uninstall), `wizard.py` (config
menu + steps), `setup_cmd.py` (preset/profile/tdd/sdd → `select`;
**agents + components → multi-select `checkbox`**), `main.py` (install wizard:
language/editor/provider `select` + API-key `secret`; all re-run/proceed
confirms; `clarify`/`clean` `input()`), and `demo_cmd`/`loop_cmd`/`privacy_cmd`/
`uninstall_cmd` confirms.

### Bugs found while testing the full surface (all fixed)

- **`menu_cmd._run_backups` crashed on entry** — `Prompt.ask` with `Prompt`
  never imported (NameError). Also was a numbered `1/2/3/4/b/q` menu.
- **`menu_cmd._run_uninstall` crashed on entry** — `Confirm.ask` with `Confirm`
  never imported (NameError). Both paths were TTY-only, so the suite never hit
  them — that is how they shipped.
- **`run_wizard_menu` hung forever on a non-TTY** — the `while True` loop exits
  only on an explicit "quit"; without a terminal the selector returns its
  default ("wizard") every iteration. `opencontext config` / `config wizard`
  reach it directly. Added the same non-TTY guard `run_main_menu` already had.
- Stale copy referencing the old numbered menu (`(option 2 to upgrade)`,
  `option 1 (Install)`); dead code (`_InstallArgs`/`_MemoryArgs`, a discarded
  `… if False else "   "` expression).

### Verification

4 gates green (ruff, ruff-format, mypy core, pytest 1695). 43/43 subcommand
`--help`; read-only commands and write paths (`setup`/`install`/`uninstall`
dry-run + real, in throwaway temp projects) exercised live. Navigable selectors
driven with **real keystrokes through a pseudo-terminal** (arrow/space/enter →
correct values for `select`, multi-select `checkbox`, and `confirm`). New tests:
`tests/core/test_prompts.py` (degradation contract) and
`tests/cli/test_menu_actions.py` (the two crash paths + the non-TTY guard).

### Full-surface sweep (round 2) — every command exercised live

All 43 subcommands and their leaves run against a real repo (read-only) and
throwaway temp projects (write paths). Broadly functional — no crashes, no
hangs. `mcp` initializes its JSON-RPC server with 13 tools; `install`/`index`/
`sync`/`setup`/`uninstall`/`clean` complete end-to-end; KG/memory/bridges/routes/
benchmark/contract/bytecode/security all return.

Three real issues found and fixed:

- **`doctor security` false positive** — the `traces.raw.disabled` check tested
  `security.mode != "developer"` instead of the actual trace setting, so a
  hardened developer-mode config (`traces.store_raw_context: false`) failed a
  security check it should pass. Now checks `not config.traces.store_raw_context`
  — matches the check's name/intent. Repo went 6/7 → 7/7. Regression test added
  (`test_traces_raw_check_reflects_actual_config_not_security_mode`).
- **`memory harvest` on empty state** exited 1 with `Error: No trace directory
  found` — empty state, not a failure. Now a graceful exit-0 message pointing at
  `opencontext loop`.
- **`preset apply <unknown>`** errored without listing valid names. Now lists the
  available presets and notes that setup presets (`context-first`, …) are a
  separate namespace.

### Refinements (round 3) — ✅ done

- **`sync all` / `sync mcp` / `sync knowledge-graph` / `sync plugins`** now work
  as subcommands (each pins `--component` via `set_defaults`), not just
  `sync --component <x>`. `issues`/`config` unchanged.
- **`knowledge-graph view`** writes the interactive HTML into `.opencontext/`
  (managed, gitignored), not the repo root. `--output` still overrides.
- **`doctor --strict`** exits non-zero when any check fails (CI gate). Verified:
  exit 1 on a config with `traces.store_raw_context: true`, exit 0 otherwise.
- **CI guard test** (`tests/cli/test_no_raw_interactive_prompts.py`): scans live
  source for `Prompt.ask`/`Confirm.ask`/`input(` (allows `prompts.py` and
  numeric `IntPrompt`). Closes the "TTY-only path, untested" regression class.
- **`run_wizard` feature toggles → one `checkbox`** (multi-select) instead of ~7
  sequential yes/no; agent integrations in both `run_wizard` and `reconfigure`
  likewise. Network features stay hidden/off in air-gapped mode.
- **`_run_configure_models`** no longer opens the whole config menu (UX mismatch)
  — the "Providers & models" entry configures provider/model directly (the dead
  fallback is now the live path).
- **`preset` discoverability** — `preset list` footer and the `preset apply`
  error both point at the separate `setup --preset` scaffolding namespace.

### Subsystem deep test (round 4) — every engine exercised via real APIs

Drove the actual engines end-to-end (not `--help`), each with assertions:

- **Agentic flow** — `HarnessRunner.run("sdd", task)` runs all 9 phases
  (EXPLORE→…→ARCHIVE), produces artifacts + gates. EXPLORE uses real KG context;
  the LLM phases emit empty artifacts under the mock provider (by design — they
  warn "configure a provider").
- **KG** — index a known project → 4 nodes, the `add←subtract` call edge,
  `search("subtract")` hits.
- **Retrieval / verified-context** — 5 gates produced, evidence grounded to the
  real source file.
- **Memory** — layered write (semantic/episodic/procedural) + recall + supersede.
- **Compression** — AICX `bytecode compile` → 93.7% reduction, checksum valid,
  `decode` round-trips the evidence list.
- **Config** — prefs → `sync_runtime_prefs_to_yaml` → yaml updated and re-validates.
- **Personas / Agents / Skills** — all 3 personas load with content; integration
  files generate per target; skill create→validate→list round-trips.
- **Engram coupling** — `detect_engram()` returns cleanly (no co-resident install
  here → local fallback, as designed).

Three real bugs found and fixed:

- **Agentic ARCHIVE phase failed on every run** — its `artifact_persisted` gate
  checked `run.json`, but the runner writes that only in `persist_run()` *after*
  all phases. Archive now writes a preliminary `run.json` itself (the runner
  finalizes it). The existing test had masked this by pre-creating the file.
  Regression test added.
- **`SQLiteMemoryBackend` didn't create its parent dir** — the public
  `BackendFactory.create_memory_store` crashed (`unable to open database file`)
  on a fresh storage path. Now `mkdir(parents=True)` defensively.
- **`skill create` crashed** — `console.ask(...)` on the dx `BrandConsole`, which
  has no `.ask()`. Now uses `prompts.text`. The CI guard was extended to flag
  `console.ask(` so this class can't recur.

### Still open (genuine product calls, not bugs)

- **`preset` namespace duality** — the two preset sets still exist (config-tuning
  vs project-scaffolding); only discoverability was improved, not merged.
- **Onboarding "perfilado":** wizards emit no step-level telemetry, so there is no
  funnel data on where users abandon setup. Wiring the existing `telemetry`
  command into wizard steps is a feature, not a fix.

---

## Engram Coexistence — ✅ Done

OpenContext memory now couples to a co-resident Engram install (the design in
Engram memory #1883: EPISODIC/SEMANTIC → Engram, PROCEDURAL/FAILURE/WORKING →
local; no duplication).

- `memory/engram_bridge.py` (new): `detect_engram()` + `EngramCliClient`
  (reads Engram's SQLite via `LIKE` — fts5-independent, read-only; writes via
  the `engram` CLI). `default_engram_client()` builds it when detected.
- `BackendFactory.create_memory_store`: `provider: auto` (default) couples to
  Engram if present, else local; `provider: engram` forces coupling (injected
  client or detected install); `local` stays local. Air-gapped → local.
- Auto-detection is suppressed under pytest and overridable via
  `OPENCONTEXT_ENGRAM=0|1` (+ `OPENCONTEXT_ENGRAM_DB`, `OPENCONTEXT_ENGRAM_PROJECT`).
- Verified live against the real `~/.engram/engram.db`: semantic/episodic recall
  pulled from Engram, procedural/working stay local, `scope=None` merges via RRF.

---

## Memory Architecture — Remaining

| System | Backend | Role | Used by |
|--------|---------|------|---------|
| `memory/` | SQLite + FTS5 | canonical agent memory (`MemoryRecord`, cognitive layers, decay/reinforce/contradict) | retrieval planner, UnifiedGraph, Engram coupling |
| `memory_usability/` | Markdown + frontmatter (`.opencontext/context-repository/`) | human-readable projection + usability layer (progressive disclosure, novelty, GC, temporal, pinning) | runtime read, harness summaries |
| `engram_mcp_store.py` + `engram_bridge.py` | Engram (CLI + SQLite) | EPISODIC/SEMANTIC backend when coupled | CompositeMemoryStore |

Relationship: `MemoryHarvester` **dual-writes** — `MemoryRecord`s to the
`AgentMemoryStore` (source of truth) and a derived human-readable summary to the
`ContextRepository`. `runtime` **dual-reads** both and reconciles by id. These are
**complementary layers, not duplicate stores** (different schema, format, and
consumers) — so they are kept separate, not merged.

### Shelf-ware cleanup — ✅ Done

Audit found 6 `memory_usability/` symbols exported but with zero consumers. Acted:
- **Deleted** (undocumented, unwired, redundant with the canonical `compression/`
  package): `code_compression.py` (`CodeCompressionPolicy`/`Decision`),
  `memory_compressor.py` (`MemoryCompressor`), `compression_quality.py`
  (`CompressionQualityGate`) + their tests + `__all__` entries.
- **Fixed an inverted dependency**: `CodeCompressionMode` (the one load-bearing
  symbol in `code_compression.py`, used by `compression/code_compressor.py`) now
  lives in `compression/code_compressor.py` where it belongs — `compression/` no
  longer imports back into `memory_usability/`.

**Open — documented but unwired (decide wire-or-cut):** `ProgressiveDisclosureMemory`,
`TemporalMemoryGraph`, `ContextDAG` have docs under `docs/memory/` but no runtime
callers. Left in place (deleting documented features is a product call); flagged so
they don't ship as silent shelf-ware.

**Open (consolidation):**
- The two stores diverge on lifecycle: SQLite `decay()` vs `memory_gc` on the
  markdown repo; reinforce/contradict only touch SQLite; supersede only the
  markdown. The derived summary can go stale vs the live records. No correctness
  bug (reconciled on read). Collapsing to one source-of-truth with a rendered view
  is a large refactor; deferred deliberately.
- No bulk export/import between OC local memory and Engram (the CLI client covers
  live read/write coupling, not migration).

---

## Compression Module — ✅ Integrated

`compression/` is wired and passes ruff + mypy:

- `OutputReducer` → `workflow/steps.py` (verbosity instruction in the prompt)
- `ContentRouter` → `context/compression.py` (CompressionEngine)
- `CacheAligner` → `context/assembler.py`
- `SmartCrusher` → `context/bytecode/compiler.py`
- `CCRCache` — global state removed; backend injected
- `CodeCompressor` → `context/compression.py` (CompressionEngine instantiates and calls it)
- `CodeCompressionMode` enum now lives in `compression/code_compressor.py` (moved out of `memory_usability/`)

---

## Items from Previous Spec Not Applied

`docs/IMPL_SPEC.md` listed 11 changes. Applied: 5. Pending: 6.

| Item | Status |
|------|--------|
| assembler.py bare except → log | ✅ Done |
| ccr_cache.py unicode → ASCII | ✅ Done |
| gates.py first_run_bypass | ✅ Done |
| comparative.py/proxy.py token estimation | ✅ Done |
| compression/__init__.py scaffold comments | ✅ Done |
| ccr_cache.py remove global state | ✅ Done |
| planner.py remove _rrf_fuse wrapper | ⏭️ Skipped — not a trivial wrapper |
| runtime.py integrate OutputReducer | ✅ Done — already wired in `workflow/steps.py` |
| engram_mcp_store.py silent exceptions → log | ✅ Done |
| planner.py silent exceptions → log | ✅ Done |
| memory/graph.py silent exceptions → log | ✅ Done |
| delegation.py scaffold → intent comment | ✅ Done |
| main.py scaffold → intent comment | ✅ Done |

---

## Action Items

### P0 — Blocking — ✅ all done

1. ✅ CI passes — `test_public_surfaces_do_not_expose_external_names` green (STATE.md reworded)
2. ✅ `.claude/worktrees/` added to `.gitignore` and `opencontext.yaml:project_index.ignore`
3. ✅ `_global_backend` removed from `compression/ccr_cache.py` — backend now injected (required param)

### P1 — Correctness — ✅ all done

4. ✅ mypy errors fixed in `compression/` and `context/bytecode/`
5. ✅ ruff errors fixed (compression/ + a `❯` glyph in `memory_usability/content_router.py`)
6. ⏭️ `_rrf_fuse` kept — it bridges non-hashable `ContextItem`s to the shared id-based RRF (one call site, well-named adapter); inlining adds noise for no gain
7. ✅ `OutputReducer` already integrated in `workflow/steps.py` (verbosity instruction wired into the assembled prompt)
8. ✅ Scaffold comments in `delegation.py` and `main.py` replaced with neutral `# NOTE:` comments
9. ✅ Silent `except Exception` → `_log.debug` in `planner.py`, `memory/graph.py`, `engram_mcp_store.py`

### P2 — Consolidation

10. ⏳ **Open decision**: merge `memory_usability/` (JSON) into `memory/` (SQLite) or keep separate — large refactor, deferred for explicit go-ahead
11. ✅ `memory.provider` set explicitly (`auto`) in `opencontext.yaml` + config default
12. ⏳ Broader `except Exception` audit across non-memory core modules (the memory/retrieval hot paths are done)
13. ⏳ Confirm `memory.harvest_after_run` behavior matches intent (repo yaml sets it `false`)

---

## Related Docs

- `docs/memory/overview.md` — Memory layer documentation
- `docs/configuration/reference.md` — Config reference
- `README.md` — Project overview
