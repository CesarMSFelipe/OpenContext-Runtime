# Trace Model

Every run produces a trace containing run identity, workflow name, input,
provider and model selection, selected and discarded context items, token
budgets, before and after token estimates, compression strategy, prompt
sections, final answer, timings, and errors. Local traces are written to
`.storage/opencontext/traces/`.

The trace also exposes OpenTelemetry-compatible fields: trace id, span id,
parent span id, span name, start/end timestamps, attributes, and events. Nested
spans are persisted for retrieval, ranking, packing, compression, prompt
assembly, generation, and trace persistence.
