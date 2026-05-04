# Specification-Driven Development (SDD) Workflow

The SDD (Specification-Driven Development) workflow is OpenContext's unified approach to context preparation that works across all technology stacks. It provides a standardized, specification-first method for gathering, validating, and packaging project context for AI-assisted development.

## Overview

The SDD workflow is designed to be **technology-agnostic**, working consistently whether you're building with Django, React, Node.js, Rust, or any other framework. It focuses on **what** needs to be done rather than **how** it's implemented in a specific technology.

### Key Principles

1. **Specification-First**: Define what you want to achieve before touching implementation
2. **Context-Aware**: Automatically discover relevant project context
3. **Safe by Default**: Validate and test all context before use
4. **Auditable**: Full traceability of context decisions
5. **Agostic**: Works across all languages, frameworks, and architectures
6. **Composable**: Each phase can be used independently or as part of the full flow

## The SDD Workflow Phases

The SDD workflow consists of seven distinct phases:

```
Explore → Propose → Apply → Test → Verify → Review → Archive
```

### 1. Explore Phase

**Purpose**: Discover and retrieve relevant project context

- Retrieves candidate files, symbols, and documentation
- Uses semantic search to find relevant code
- Ranks candidates by relevance to the task
- Identifies potential dependencies and connections

**CLI Usage**:
```bash
opencontext sdd explore "Implement user authentication" --root . --max-tokens 8000
```

**API Endpoint**:
```bash
POST /v1/context
```

**What It Produces**:
- List of candidate context sources
- Relevance scores for each source
- Token estimates for the exploration

### 2. Propose Phase

**Purpose**: Create a token-aware context pack proposal

- Packages the most relevant context within token budgets
- Prioritizes high-value sources (P0, P1 priorities)
- Applies compression where beneficial
- Validates against safety policies

**CLI Usage**:
```bash
opencontext sdd propose "Review authentication implementation" --root .
```

**What It Produces**:
- Context pack with included/omitted sources
- Token usage breakdown
- Justification for inclusions/omissions
- Safety validation results

### 3. Apply Phase (Optional)

**Purpose**: Execute proposed changes with safety gates

- Integrates with OpenContext's action system
- Respects security policies and egress controls
- Can execute safe commands, file writes, and tests
- Requires approval for high-risk operations

**CLI Usage**:
```bash
opencontext sdd apply sdd_apply --root .
```

**What It Produces**:
- Execution results
- Audit trail of all actions
- Any generated artifacts
- Approval records

### 4. Test Phase

**Purpose**: Validate context pack safety and integrity

- Checks classification invariants
- Validates against security policies
- Ensures no secrets in context
- Verifies token budgets respected

**CLI Usage**:
```bash
opencontext sdd test --root .
```

**What It Produces**:
- Pass/fail status
- Detailed validation results
- Security check outcomes
- Remediation suggestions

### 5. Verify Phase

**Purpose**: Comprehensive security and quality verification

- Runs security scans on proposed context
- Checks for policy violations
- Validates data classification compliance
- Ensures no sensitive data exposure

**CLI Usage**:
```bash
opencontext sdd verify --root .
```

**What It Produces**:
- Security scan results
- Severity assessment
- Findings and recommendations
- Approval status

### 6. Review Phase

**Purpose**: Final review and approval before deployment

- Checks for high-risk items
- Validates all previous phases
- Provides approval/rejection decision
- Creates audit record

**CLI Usage**:
```bash
opencontext sdd review --root .
```

**What It Produces**:
- Approval decision
- Risk assessment
- Review trail
- Deployment readiness status

### 7. Archive Phase

**Purpose**: Persist and clean up

- Archives context pack for future reference
- Creates immutable record
- Links to trace for auditability
- Cleans up temporary resources

**CLI Usage**:
```bash
opencontext sdd archive --root .
```

**What It Produces**:
- Archived context pack
- Trace ID for reference
- Metadata for retrieval
- Audit record

## Complete SDD Flow

Run all phases in sequence:

```bash
opencontext sdd flow "Implement OAuth2 authentication" --root . --max-tokens 8000
```

This executes the entire pipeline:
1. Explore → 2. Propose → 3. Apply → 4. Test → 5. Verify → 6. Review → 7. Archive

## Workflows

OpenContext provides two pre-configured SDD workflows:

### sdd Workflow

The basic SDD workflow for context preparation:
```yaml
workflows:
  sdd:
    steps:
      - project.load_manifest
      - context.explore
      - context.propose
      - context.test
      - context.verify
      - context.review
      - context.archive
      - trace.sdd_persist
```

### sdd_apply Workflow

The full SDD workflow including execution:
```yaml
workflows:
  sdd_apply:
    steps:
      - project.load_manifest
      - context.explore
      - context.propose
      - context.apply
      - context.test
      - context.verify
      - context.review
      - context.up-code
      - context.archive
      - trace.sdd_persist
```

## API Integration

### Run SDD Flow via API

```bash
curl -X POST http://localhost:8000/v1/refactor/sdd \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Implement authentication",
    "root": "/path/to/project",
    "max_tokens": 8000,
    "refresh_index": false
  }'
```

### Response

```json
{
  "status": "completed",
  "result": {
    "mode": "sdd",
    "trace_id": "abc123...",
    "query": "Implement authentication",
    "context": "...",
    "included_sources": ["src/auth.py", "src/models.py"],
    "omitted_sources": [],
    "token_usage": {
      "selected_after_optimization": 2500,
      "prompt": 150
    },
    "raw_secrets_included": false,
    "safety": {
      "test_allowed": true,
      "security_scan_severity": "none",
      "security_findings": 0,
      "high_risk_files": 0,
      "review_status": "approved"
    }
  }
}
```

## Technology Agnosticism

The SDD workflow works identically across all technology stacks:

### Python/Django
```bash
opencontext sdd flow "Create user registration endpoint"
```

### Node.js/Express
```bash
opencontext sdd flow "Add JWT authentication middleware"
```

### React/TypeScript
```bash
opencontext sdd flow "Implement login form with validation"
```

### Rust/Actix
```bash
opencontext sdd flow "Add session management"
```

All use the same workflow, same phases, same safety checks. The only difference is the **project context** discovered during the Explore phase.

## Integration with Agents

The SDD workflow integrates seamlessly with any AI agent:

### Claude Code
```bash
opencontext agent-context "Implement auth" --target claude-code
```

### Cursor
```bash
opencontext agent-context "Add OAuth2" --target cursor
```

### Custom Agents
```bash
opencontext agent-context "Task" --target generic
```

All agents receive the same standardized context envelope.

## Safety and Compliance

The SDD workflow enforces:

- **Classification Checks**: Validates data classification at each phase
- **Policy Enforcement**: Respects organization security policies
- **Token Budgets**: Prevents context overflow
- **Audit Trails**: Complete traceability of all decisions
- **Secret Detection**: Automatic redaction of sensitive data
- **Egress Controls**: Prevents unauthorized data export

## Best Practices

1. **Start Small**: Run explore + propose before full flow
2. **Iterate**: Use phases independently for complex tasks
3. **Review**: Always check review phase before deployment
4. **Archive**: Keep archives for audit and learning
5. **Customize**: Create custom workflows for your needs

## Troubleshooting

### Context Too Large
```bash
opencontext sdd explore --max-tokens 4000
```

### High-Risk Items Detected
Check review phase output and adjust context

### Policy Violations
Review security policies and adjust context sources

### Token Budget Exceeded
Use compression or reduce included sources

## See Also

- [Workflow Engine](./workflow-engine.md)
- [Context Packing](./architecture/context-pack-builder.md)
- [Safety Layer](./architecture/safety-layer.md)
- [Custom Workflows](./custom-workflows.md)
- [Provider Policies](./security/provider-policies.md)
