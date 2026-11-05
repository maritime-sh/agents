#!/usr/bin/env python3
"""Deploy browser-use to a Maritime Linux desktop and run one task.

    export MARITIME_API_KEY=mk_...
    export ANTHROPIC_API_KEY=sk-ant-...     # or OPENAI_API_KEY, or GOOGLE_API_KEY
    python3 deploy.py "Go to maritime.sh/pricing and tell me what the Growth plan costs"

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

ENV = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "GOOGLE_API_KEY",
       "BROWSER_USE_MODEL", "BROWSER_USE_MAX_STEPS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?",
                        default="Go to maritime.sh/pricing and tell me what the Growth plan costs a month.")
    parser.add_argument("--name", default="browser-use", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    if not args.install_only and not any(os.environ.get(v) for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY")):
        sys.exit("Set ANTHROPIC_API_KEY, OPENAI_API_KEY or GOOGLE_API_KEY for the model.")
    return deploy(
        slug="browser-use",
        computer_name=args.name,
        agent_dir=HERE / "agent",
        env_vars=ENV,
        run_command=None if args.install_only else ".venv/bin/python run.py",
        task=args.task,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
