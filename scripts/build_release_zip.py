#!/usr/bin/env python3
"""Build a clean source release ZIP via git archive."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path, ref: str = "HEAD") -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "archive",
            "--worktree-attributes",
            "--format=zip",
            f"--output={output}",
            ref,
        ],
        check=True,
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / "OpenContext-Runtime.zip",
        help="Output ZIP path.",
    )
    parser.add_argument("--ref", default="HEAD", help="Git ref to archive.")
    args = parser.parse_args()
    out = build(args.output, args.ref)
    print(f"Built {out}")


if __name__ == "__main__":
    main()
