# opencontext-core

Core, provider-neutral runtime for OpenContext Runtime.

This package contains project indexing, retrieval, context packing, redaction, prompt assembly,
trace persistence, safety policy checks, and runtime-first setup APIs. It intentionally avoids
FastAPI, CLI framework imports, provider SDKs, vector databases, LangChain, and LlamaIndex.

Most integrations should start with:

```python
from opencontext_core import OpenContextRuntime

runtime = OpenContextRuntime()
runtime.setup_project(".")
prepared = runtime.prepare_context("Review authentication", max_tokens=6000)
```
