# opencontext-api

FastAPI adapter for OpenContext Runtime.

Use this package when a non-Python host needs HTTP endpoints for runtime-first setup and context
preparation:

- `POST /v1/setup`
- `POST /v1/context`
- `GET /v1/traces/{trace_id}`

The API is intentionally thin and delegates context behavior to `opencontext-core`.
