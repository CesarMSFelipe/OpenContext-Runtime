# Workflow Engine

Workflows are named YAML step lists. The v0.1 runtime ships these steps:

- `project.load_manifest`
- `project.retrieve`
- `context.rank`
- `context.pack`
- `context.compress`
- `prompt.assemble`
- `llm.generate`
- `trace.persist`

Unknown steps raise a configuration error. Steps are registered explicitly so
new workflows can be added without changing the runtime facade.
