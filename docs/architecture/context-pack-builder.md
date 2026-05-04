# Context Pack Builder

`ContextPackBuilder` is the hard budget gate between ranking and compression. It
orders candidates by priority, score, value per token, source trust, and stable
identifier. Included and omitted items are returned in a `ContextPackResult`.

Every omission records the item id, reason, token estimate, and score. Workflow
traces persist the full packing result so downstream users can inspect why
context was included or discarded.

