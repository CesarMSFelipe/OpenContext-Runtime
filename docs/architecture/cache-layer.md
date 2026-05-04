# Cache Layer

The cache layer defines conservative interfaces without provider dependencies.
`CacheKey` includes workflow name, project hash, model name, prompt version,
normalized input hash, and context hash. `ExactPromptCache` is an in-memory exact
cache. `SemanticCache` is only an interface and is disabled by default.

