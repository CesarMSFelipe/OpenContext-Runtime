# Evaluation Layer

The evaluation layer is a v0.1 skeleton for future CI and quality gates.
`EvalCase` captures workflow, input, expected or forbidden sources, and behavior
notes. `BasicEvaluator` performs structural checks only and does not call an
LLM.

The CLI command `opencontext eval run <path>` reads YAML or JSON cases and emits
basic results.

