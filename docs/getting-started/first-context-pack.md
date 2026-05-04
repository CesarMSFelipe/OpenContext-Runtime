# First Context Pack

## Purpose
Explain the first useful `opencontext pack` workflow.

## Current Status
Context packs are local-only by default. A pack contains sources, security warnings, token stats, included context, and omissions. Retrieved content is wrapped as untrusted data.

## Commands
```bash
opencontext index .
opencontext pack . --query "Review access control" --mode review --max-tokens 6000
opencontext pack . --query "Review access control" --format toon
```

## Implemented Code
- Pack builder: `packages/opencontext_core/opencontext_core/context/packing.py`
- CLI rendering: `packages/opencontext_cli/opencontext_cli/main.py`
- Serializer: `packages/opencontext_core/opencontext_core/memory_usability/serializers.py`
