---
name: oc-new
description: Start a new change — automatically runs the full SDD flow end to end.
triggers:
  - oc-new
  - new change
  - start a change
  - new feature
version: 0.1.0
---

# oc-new

Start a new SDD change and **drive the whole flow automatically**. This is the
single entry point: it runs every phase in order, switching to the right persona
for each, pausing only at the approval gate before writing code.

## When to use

At the very beginning of a change, when the developer describes a feature, bug
fix, or refactor. Prefer this over invoking each phase by hand.

## Flow (run automatically, in order)

Create a `trace_id` and carry it through every phase.

1. **oc-explore** (OC Explorer) — map the code with `opencontext_context` /
   `opencontext_impact`; produce the verified context pack.
2. **oc-propose** (OC Orchestrator) — intent, scope, affected areas, non-goals.
3. **oc-spec** (OC Orchestrator) — requirements (RFC 2119) + GIVEN/WHEN/THEN.
4. **oc-design** (OC Architect) — architecture, components, data flow, test strategy.
5. **oc-tasks** (OC Orchestrator) — ordered, verifiable checklist (TDD-first).
6. **Approval gate** — show the plan; proceed only on approval (or `--yes`).
7. **oc-apply** (OC Builder + OC Tester) — tests first, then implementation.
8. **oc-verify** (OC Reviewer) — run tests + gates.
9. **oc-archive** — persist run/memory/graph deltas; the KG is rebuilt with the
   change.

The single-process equivalent is `opencontext loop --task "<change>" --flow full`.

## Rules

1. Run the phases in order without waiting for the user to invoke each one; the
   only stop is the approval gate before code is written.
2. Carry one `trace_id` across all phases.
3. Each phase adopts its persona and passes its gates before the next begins; a
   failed gate stops the chain — report it, do not route around it.
4. Never write production code before the spec, design, and approval exist.
