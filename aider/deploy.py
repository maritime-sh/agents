#!/usr/bin/env python3
"""Deploy Aider to a Maritime Linux desktop and run one coding task.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=sk-...            # plus OPENAI_BASE_URL for any OpenAI-compatible endpoint
    python3 deploy.py "Write fizzbuzz.py and a unittest for it, then run the test."

Each task gets a fresh git repo under /data/projects on the computer. Aider runs in a
terminal window on the desktop, so you can watch it live. Run it again with another
task: the same computer is reused, already installed.
"""

import argparse
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from linux_agent import deploy  # noqa: E402
from maritime_computer import MaritimeError  # noqa: E402

ENV = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "AIDER_MODEL")
DEFAULT_TASK = ("Write primes.py with a function is_prime(n), and test_primes.py with unittest cases "
                "for a few primes and non-primes.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?", default=DEFAULT_TASK)
    parser.add_argument("--name", default="aider", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    if not args.install_only and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for any OpenAI-compatible endpoint).")
    return deploy(
        slug="aider",
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
