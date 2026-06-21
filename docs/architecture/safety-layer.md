# Safety Layer

The safety layer implements:

- `SecretScanner` — detects and redacts OpenAI, Anthropic, GitHub, AWS,
  private-key blocks, database URLs, JWT-like tokens, Slack, Google, and Stripe
  keys, plus generic `*SECRET/TOKEN/PASSWORD/API_KEY/DATABASE_URL=` env secrets.
  Indexing marks files with potential secrets in manifest metadata; retrieval
  redacts secret values before context enters a prompt.
- `BasicPiiScanner` — flags email, phone, and Luhn-validated credit-card numbers.
- `PromptInjectionScanner` — flags known injection phrases (e.g. "ignore previous
  instructions"); `render_untrusted_context` wraps untrusted content as
  non-authoritative evidence. Findings surface as non-blocking warnings from
  `ContextFirewall`.
- `ContextFirewall` — fail-closed gate over context export, provider calls, and
  trace persistence; secret-bearing context is redacted in place or hard-blocked.
- Provider and tool policies — enforced via `ProviderPolicyEnforcer` before any
  LLM call.

Output schema validation remains a future boundary.
