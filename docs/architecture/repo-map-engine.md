# Repo Map Engine

The repo map gives the runtime a compact project overview before full files are
loaded. It renders file paths and extracted symbols only; raw file contents are
never included in the map.

Entries are ranked by query matches in paths and symbols, with a small boost for
structural files such as config, route, controller, service, repository,
middleware, and adapter files.
`RepoMapEngine.render()` can enforce a token budget so the map can sit in the
stable prompt prefix.

## Relationship To Retrieval

The repo map is the first overview layer. It gives the model project shape and symbol locations
without raw source. Retrieval can then load a small set of high-signal context items. Static
dependency graph metadata and optional cross-project graph tunnels can improve recall, but raw file
content is still selected and packed under the same budget and redaction rules.
