# Ai Team Operating Model

## Purpose
A team-grade AI operating layer compiles context, policy, tools, memory, approvals, cache, and evaluation into repeatable workflows.

## Current Status
Local scaffolds are implemented for command registry, hook registry, approvals, playbooks, baselines, policy diff, run receipts, and reports. They do not execute external actions by default.

## Related Commands
```bash
opencontext playbooks list
opencontext command run review-pr
opencontext approvals list
opencontext run receipt last
opencontext policy diff main..HEAD
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/operating_model/team.py`
