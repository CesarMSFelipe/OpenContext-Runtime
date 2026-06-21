# Workflow Engine

Workflows are named YAML step lists. The runtime ships these core steps:

- `project.load_manifest`
- `project.retrieve`
- `context.rank`
- `context.pack`
- `context.compress`
- `prompt.assemble`
- `llm.generate`
- `trace.persist`

The SDD workflow adds these steps (see [SDD workflow](../workflows/sdd-workflow.md)):

- `context.explore`
- `context.propose`
- `context.apply`
- `context.test`
- `context.verify`
- `context.review`
- `context.archive`
- `context.up-code`
- `trace.sdd_persist`
- `embeddings.generate`

Unknown steps raise a configuration error. Steps are registered explicitly so
new workflows can be added without changing the runtime facade.
