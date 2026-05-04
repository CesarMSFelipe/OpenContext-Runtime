# SOC 2 Control Mapping Notes

These notes describe how OpenContext Runtime can support SOC 2 evidence. They
are not a SOC 2 report.

## Security

- Deny-by-default tools, writes, network, and MCP.
- Provider policy enforcement and air-gapped mode.
- Secret redaction before prompts, traces, and context exports.

## Confidentiality

- Data classifications on context and prompt models.
- Sanitized trace persistence by default.
- Raw secret values excluded from scan reports.

## Processing Integrity

- Deterministic indexing, retrieval, ranking, and packing tests.
- Token budgets and omission reasons captured in traces.
- CLI/API smoke tests for core workflows.

## Availability

- Local-only mock mode and no API key required for first run.
- Remaining work: operational SLOs and hosted deployment runbooks.
