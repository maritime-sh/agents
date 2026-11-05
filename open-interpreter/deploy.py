#!/usr/bin/env python3
"""Deploy Open Interpreter to a Maritime Linux desktop and run one task.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=sk-...            # plus OPENAI_BASE_URL for any OpenAI-compatible endpoint
    python3 deploy.py "Make a bar chart of the planets by diameter and open it in Chromium."

Open Interpreter writes and runs code on the computer, without asking first: the computer
is its own. It runs in a terminal window on the desktop, and the windows it opens show
up there too, so you can watch it live. Run it again with another task: the same
computer is reused, already installed.
"""

import argparse
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from linux_agent import deploy  # noqa: E402
from maritime_computer import MaritimeError  # noqa: E402

ENV = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "INTERPRETER_MODEL")
DEFAULT_TASK = ("Make a bar chart of the eight planets by diameter with matplotlib, save it as planets.png, "
                "and open it in Chromium.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?", default=DEFAULT_TASK)
    parser.add_argument("--name", default="open-interpreter", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    if not args.install_only and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for any OpenAI-compatible endpoint).")
    return deploy(
        slug="open-interpreter",
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
