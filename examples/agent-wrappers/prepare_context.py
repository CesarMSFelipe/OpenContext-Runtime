"""Prepare compact OpenContext input for an external coding agent.

This script is intentionally provider-neutral. It indexes the project when
needed, prepares task-specific context, and writes a markdown payload that can be
used by Codex, Claude Code, OpenCode, or a custom adapter.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from opencontext_core.runtime import OpenContextRuntime, PreparedContext


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--task", required=True, help="Developer task for the agent.")
    parser.add_argument("--config", default=None, help="Optional opencontext.yaml path.")
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--output", required=True, help="Markdown output path.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    runtime = OpenContextRuntime(config_path=args.config)
    prepared = runtime.prepare_context(
        args.task,
        root=root,
        max_tokens=args.max_tokens,
        refresh_index=True,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_payload(args.task, prepared), encoding="utf-8")


def render_payload(task: str, prepared: PreparedContext) -> str:
    included = "\n".join(f"- {source}" for source in prepared.included_sources)
    omitted = "\n".join(f"- {source}" for source in prepared.omitted_sources)
    return f"""# Task

{task}

# OpenContext Trace

- trace_id: {prepared.trace_id}
- context_tokens: {prepared.token_usage.get("final_context_pack", 0)}

# Included Sources

{included}

# Omitted Sources

{omitted or "- none"}

# Prepared Context

{prepared.context}
"""


if __name__ == "__main__":
    main()
