# Observability

Local traces are persisted as JSON under `.storage/opencontext/traces/`. The
trace model keeps the previous runtime fields and adds OpenTelemetry-compatible
concepts: trace id, span id, parent span id, span name, start and end times,
attributes, and events.

Workflow traces include spans for project retrieval, ranking, packing,
compression, prompt assembly, LLM generation, and trace persistence. Context
packing decisions and prompt sections are stored directly in the trace.

