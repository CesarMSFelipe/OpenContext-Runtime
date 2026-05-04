# Context Optimization Layer

The context optimization layer ranks candidate context with this deterministic
formula:

```text
score =
  relevance_weight * retrieval_relevance
  + priority_weight * priority_score
  + source_trust_weight * source_trust
  + token_efficiency_weight * token_efficiency
  + recency_bonus
```

`priority_score` maps P0 to `1.0` and P5 to `0.0`. `token_efficiency` favors
shorter high-signal items. `recency_bonus` is small and only applies when a
timestamp is present. Compression is explicitly lossy unless the `none` strategy
is used.

Before compression, `ContextPackBuilder` applies the hard context budget. It
sorts by priority, score, value per token, source trust, and stable id. Omitted
items are traceable through `ContextOmission` records. Protected spans then
prevent compression from mutating code blocks, schemas, numeric values, file
paths, citations, and warning-like text.
