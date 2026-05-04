# opencontext-providers

Optional provider adapter package for OpenContext Runtime.

Core remains provider-neutral. Real external provider integrations should live outside
`opencontext-core`, be explicitly enabled by policy, and preserve redaction, trace, and
classification controls.
