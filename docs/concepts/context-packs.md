# Context Packs

## Purpose
Context packs contain selected sources, token stats, security warnings, untrusted content wrappers, and omission reasons. They are safe local artifacts intended for coding agents and audits.

## Current Status
Implemented through `OpenContextRuntime.prepare_context()` and `opencontext pack`. A context pack
contains selected source snippets or summaries, included and omitted source lists, omission reasons,
token accounting, redaction metadata, and a trace id. Retrieved content is treated as untrusted
evidence and cannot override system, developer, workflow, or security policy instructions.

Context packs are the default artifact to hand to Codex, Claude Code, Cursor, Windsurf, OpenCode, or
a custom agent instead of dumping the whole repository into a prompt.

## Related Commands
```bash
opencontext index .
opencontext inspect repomap
opencontext pack . --query "review auth"
opencontext doctor tokens
```

## Implemented Code
- `packages/opencontext_core/opencontext_core/context/`
- `packages/opencontext_core/opencontext_core/indexing/`
- `packages/opencontext_core/opencontext_core/memory_usability/`
