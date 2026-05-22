"""Agent system for OpenContext Runtime.

This module provides an agent-based interface to OpenContext without requiring CLI.
Agents are configured via YAML profiles in .agents/profiles/ and handle:
- Automatic token management
- Memory persistence
- Index caching
- Analysis orchestration

Example usage (no CLI required):

    from opencontext_core.agents import AgentOrchestrator

    orchestrator = AgentOrchestrator(project_root=".")

    # Run code review analysis
    result = orchestrator.run_agent("code-review")
    print(result.report)

    # Run security audit
    result = orchestrator.run_agent("security-audit")
    print(result.metrics)
"""

from .base import BaseAgent
from .loader import list_available_agents, load_agent_config
from .orchestrator import AgentOrchestrator, AgentResult

__all__ = [
    "AgentOrchestrator",
    "AgentResult",
    "BaseAgent",
    "list_available_agents",
    "load_agent_config",
]
