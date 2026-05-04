# Repository Guidelines

## Project Purpose
OpenContext Runtime is a Python 3.12+ context engineering runtime for LLM
applications. It indexes projects, builds compact repo maps, retrieves and packs
high-signal context, compresses safely under token budgets, assembles
cache-friendly prompts, routes requests through an LLM gateway abstraction, and
persists traces. It is not a chatbot, a UI, a RAG wrapper, or a prompt template
collection.

## Project Structure & Package Boundaries
Core domain code lives in `packages/opencontext_core/opencontext_core`. Keep it
independent from FastAPI, CLI frameworks, provider SDKs, and storage-specific
assumptions. `packages/opencontext_api` may depend on core and exposes thin
FastAPI endpoints. `packages/opencontext_cli` may depend on core and provides
command-line entry points. Cache, safety, tools, and evaluation modules are core
interfaces only unless explicitly implemented. Tests live in `tests/core`; docs
and architecture notes live under `docs/`.

## Build, Test, and Development Commands
Install for local development with:

```bash
python3 -m pip install -e packages/opencontext_core -e packages/opencontext_cli -e packages/opencontext_api
```

Run validation from the repository root:

```bash
pytest
ruff check .
ruff format --check .
mypy packages/opencontext_core
```

Run a single test with `pytest tests/core/test_runtime.py`.

## Coding Style & Architecture Rules
Use strict typing, Pydantic v2 public models, deterministic algorithms, and
explicit interfaces. Keep decision-making traceable through metadata or trace
models. Prefer small modules with clear package ownership over shared global
helpers. Public models need docstrings and `Field` descriptions for important
attributes.

## Do Not
Do not add LangChain, LlamaIndex, OpenAI SDKs, vector databases, Docker Compose,
Kubernetes, UI code, hidden global state, or real API calls in tests. Do not put
FastAPI or CLI imports in `opencontext_core`.

## Validation Checklist
Before handing off, verify indexing, repo maps, context packing, workflow
execution, trace persistence, token-budget enforcement, deterministic ranking
and compression, README command accuracy, and clean `pytest`, `ruff`, and core
`mypy` runs.
