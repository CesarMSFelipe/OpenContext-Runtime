# Safety Layer

The safety layer currently implements `SecretScanner`. It detects common
OpenAI-like keys, GitHub tokens, AWS access keys, private key blocks, and
generic environment-variable secrets. Indexing marks files with potential
secrets in manifest metadata. Retrieval redacts secret values before context can
enter a prompt.

Prompt-injection detection and output schema validation are explicit future
boundaries and are disabled in v0.1.

