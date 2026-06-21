# Python Sdk

## Purpose
Use `OpenContextRuntime` directly for Python integration. Keep provider SDKs outside core.

## Current Status
CLI/API/local SDK paths are implemented. Agent-specific integrations are documented patterns unless a command explicitly exists.

## Usage
```python
from opencontext_core.runtime import OpenContextRuntime

rt = OpenContextRuntime(storage_path=".storage/opencontext")
rt.index_project(".")
pack = rt.build_context_pack("review auth")
```

Source: `packages/opencontext_core/opencontext_core/runtime.py`
