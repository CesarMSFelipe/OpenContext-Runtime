# OWASP LLM Controls Notes

OpenContext Runtime maps its MVP controls to OWASP LLM risk themes as follows.
This is implementation evidence, not a third-party assessment.

## Covered In MVP

- Prompt injection: retrieved context is wrapped as untrusted evidence and
  prompt-injection phrases are flagged.
- Sensitive information disclosure: secret scanning, redaction, sanitized traces,
  and context export checks are enabled by default.
- Excessive agency: tools, network, writes, and MCP are denied by default.
- Insecure plugin design: plugin and tool manifests default to no permissions.
- Supply chain: workflow packs are local scaffolds and cannot silently weaken
  policy.

## Remaining Work

- External DLP provider adapters.
- Formal adversarial eval corpus.
- Signed workflow pack verification.
