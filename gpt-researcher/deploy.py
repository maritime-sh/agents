#!/usr/bin/env python3
"""Deploy GPT Researcher to a Maritime Linux desktop and research one question.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=...            # plus OPENAI_BASE_URL for any OpenAI-compatible endpoint
    python3 deploy.py "What is the Model Context Protocol and which AI companies support it?"

The run happens in a terminal on the desktop you can watch live, and the
finished report opens in a text editor there. It is also printed here.
Run it again with another question: the same computer is reused, already installed.
"""

import argparse
import os
import pathlib
import shlex
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from maritime_computer import Computer, MaritimeError  # noqa: E402

HOME = "/data/agents/gpt-researcher"
ENV = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "TAVILY_API_KEY", "RETRIEVER",
       "FAST_LLM", "SMART_LLM", "STRATEGIC_LLM", "EMBEDDING", "TOTAL_WORDS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("question", nargs="?",
                        default="What is the Model Context Protocol and which AI companies support it?")
    parser.add_argument("--name", default="gpt-researcher", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    if not args.install_only and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for an OpenAI-compatible endpoint).")

    print(f"1/4 Getting the Linux desktop '{args.name}' ...", flush=True)
    pc = Computer.get_or_create(args.name, os="linux")
    print(f"    computer {pc.id}")
    print(f"    watch live: {pc.watch_link()}", flush=True)

    print("2/4 Installing GPT Researcher (the first run takes a few minutes) ...", flush=True)
    pc.sh(f"mkdir -p {HOME}")
    for path in sorted((HERE / "agent").iterdir()):
        if path.is_file():
            pc.write_file(f"{HOME}/{path.name}", path.read_bytes())
    pc.background(f"bash {HOME}/install.sh", f"{HOME}/install.log")
    out = pc.wait_for(f"tail -n 3 {HOME}/install.log", "MARITIME_AGENT_READY", label="installing")
    print("    " + out.strip().splitlines()[-1])
    if args.install_only:
        return 0

    print("3/4 Passing your model key (kept in /data, readable only by the desktop user) ...", flush=True)
    lines = "".join(f"export {v}={shlex.quote(os.environ[v])}\n" for v in ENV if os.environ.get(v))
    pc.write_file(f"{HOME}/.env", lines)
    pc.sh(f"chmod 600 {HOME}/.env")

    print(f"4/4 Researching: {args.question}", flush=True)
    log = f"{HOME}/run-{int(time.time())}.log"
    inner = f"bash {HOME}/show.sh {log} {shlex.quote(args.question)}"
    pc.background(
        "export DISPLAY=:1; pkill -x mousepad; "
        f"xfce4-terminal --maximize --title 'GPT Researcher' --hide-menubar -x bash -c {shlex.quote(inner)}",
        f"{HOME}/terminal.log",
    )
    pc.wait_for(f"test -f {log} && echo started", "started", timeout_s=120, every_s=3, label="")
    seen = 0
    while True:
        out = pc.sh(f"cat {log} 2>/dev/null", check=False)
        if len(out) > seen:
            sys.stdout.write(out[seen:])
            sys.stdout.flush()
            seen = len(out)
        if "MARITIME_RUN_EXIT" in out:
            return 0 if "=== SUCCESS ===" in out else 1
        time.sleep(5)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
