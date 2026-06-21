# Ai Leak And Prompt Security

## Purpose
Prompt/config leaks are assumed. Prompts must not contain secrets, tool schemas should avoid sensitive internals, and release artifacts are scanned for source maps, env files, raw traces, and AI config leaks. Implemented scaffolds live in `opencontext_core.operating_model.ai_leak`.

## Related Commands
```bash
opencontext prompt audit .
```
See [security commands and implemented code](index.md) for the full list.
