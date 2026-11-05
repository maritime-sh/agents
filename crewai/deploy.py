#!/usr/bin/env python3
"""Deploy a two-agent crewAI crew to a Maritime Linux desktop and answer one question.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=sk-...              # any OpenAI-compatible endpoint
    export OPENAI_BASE_URL=https://...        # optional
    python3 deploy.py "When was the Python programming language first released?"

Run it again with another task: the same computer is reused, already installed.
"""

import argparse
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from linux_agent import deploy  # noqa: E402
from maritime_computer import MaritimeError  # noqa: E402

ENV = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "CREWAI_MODEL")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?",
                        default="When was the Python programming language first released?")
    parser.add_argument("--name", default="crewai", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    if not args.install_only and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for another OpenAI-compatible endpoint) for the model.")
    return deploy(
        slug="crewai",
        computer_name=args.name,
        agent_dir=HERE / "agent",
        env_vars=ENV,
        run_command=None if args.install_only else "bash run.sh",
        task=args.task,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
