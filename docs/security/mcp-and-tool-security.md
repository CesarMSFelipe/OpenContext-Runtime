# MCP and Tool Security

MCP execution is disabled by default. Native tools require allowlisting and capability permissions.
The core contains policy models, a native registry boundary, sanitized output wrapping, an MCP
response compression boundary, and controlled harness preflight planning. It does not enable
unrestricted external tool execution.

The controlled action policy is fail-closed:

- read context, files, sanitized traces, and git diffs are allowed within the workspace boundary,
- safe commands, tests, linters, external providers, and allowlisted tools require approval,
- file writes require an explicit sandbox, an allowlisted target, and approval,
- network and MCP actions are denied by default,
- air-gapped mode blocks external providers, network tools, and MCP.

## Tool Decision Pipeline

Tool decisions are traceable. A call is evaluated through deny rules, tool permission checks, bypass
mode, always-allow rules, read-only checks, default mode checks, write capability, network
capability, and human approval requirements. Tool outputs are sanitized and wrapped as untrusted
context before they can be forwarded to prompt assembly or traces.

## MCP Compression Boundary

MCP response compression is implemented as a future adapter boundary. It can recursively compress
large textual response fields while preserving structured values, but MCP transport and execution
remain disabled unless a host explicitly implements and allows them.
