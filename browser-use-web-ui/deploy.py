#!/usr/bin/env python3
"""Deploy browser-use Web UI to a Maritime Linux desktop and open it there.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=...            # plus OPENAI_BASE_URL for any OpenAI-compatible endpoint
    python3 deploy.py                    # install, start, open the UI on the desktop
    python3 deploy.py "Go to news.ycombinator.com and tell me the top story"   # also type and run a task

The Web UI runs on the desktop's own Chromium; the agent opens a second
Chromium window next to it. Open the watch link the script prints to see both,
or take over the screen to use the UI yourself.
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

HOME = "/data/agents/browser-use-web-ui"
APP = f"{HOME}/web-ui-3.0.0"
# Key names the Web UI reads (see upstream .env.example), mapped from yours.
KEYS = {"OPENAI_API_KEY": "OPENAI_API_KEY", "OPENAI_BASE_URL": "OPENAI_ENDPOINT",
        "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY", "GOOGLE_API_KEY": "GOOGLE_API_KEY",
        "DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY", "MISTRAL_API_KEY": "MISTRAL_API_KEY"}
SETTINGS = {
    "ANONYMIZED_TELEMETRY": "false",
    "GRADIO_ANALYTICS_ENABLED": "False",
    "USE_OWN_BROWSER": "true",                 # the desktop's Chromium, on its screen
    "BROWSER_PATH": "/usr/bin/chromium",
    "BROWSER_USER_DATA": f"{HOME}/profile",    # the agent's logins survive sleep and restarts
    "KEEP_BROWSER_OPEN": "false",
}
# Where the Web UI's controls sit on the 1280x800 desktop (window maximized, zoom 0.67).
RUN_AGENT_TAB = (442, 133)
TASK_BOX = (635, 629)
SUBMIT = (921, 688)


def default_llm() -> str:
    for key, provider in (("OPENAI_API_KEY", "openai"), ("ANTHROPIC_API_KEY", "anthropic"),
                          ("GOOGLE_API_KEY", "google"), ("DEEPSEEK_API_KEY", "deepseek")):
        if os.environ.get(key):
            return provider
    sys.exit("Set OPENAI_API_KEY (plus OPENAI_BASE_URL), ANTHROPIC_API_KEY, GOOGLE_API_KEY or DEEPSEEK_API_KEY.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?", help="optional: a task to type into the UI and run")
    parser.add_argument("--name", default="browser-use-web-ui", help="computer name, reused on every run")
    parser.add_argument("--install-only", action="store_true")
    args = parser.parse_args()
    llm = None if args.install_only else default_llm()

    print(f"1/4 Getting the Linux desktop '{args.name}' ...", flush=True)
    pc = Computer.get_or_create(args.name, os="linux")
    print(f"    computer {pc.id}")
    print(f"    watch live: {pc.watch_link()}", flush=True)

    print("2/4 Installing browser-use Web UI (the first run takes a few minutes) ...", flush=True)
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
    env = {KEYS[k]: v for k, v in os.environ.items() if k in KEYS and v}
    env.update(SETTINGS, DEFAULT_LLM=llm)
    pc.write_file(f"{APP}/.env", "".join(f"{k}={shlex.quote(v)}\n" for k, v in env.items()))
    pc.sh(f"chmod 600 {APP}/.env; pkill -f 'webui.py --ip' ; true")  # restart so it reads the new .env

    print("4/4 Starting the Web UI and opening it in the desktop's Chromium ...", flush=True)
    pc.background(f"bash {HOME}/start.sh", f"{HOME}/start.log")
    pc.wait_for(f"cat {HOME}/start.log", "MARITIME_UI_READY", timeout_s=240, every_s=5, label="starting")
    time.sleep(8)
    print("    The Web UI is open on the desktop (http://127.0.0.1:7788 inside the computer).")
    if not args.task:
        print("    Open the watch link above, or take over the screen, to use it.")
        return 0

    print(f"    Typing the task into Run Agent: {args.task}", flush=True)
    started = pc.sh("date +%s").strip()
    x = "DISPLAY=:1 xdotool"
    pc.sh(f"{x} mousemove {RUN_AGENT_TAB[0]} {RUN_AGENT_TAB[1]} click 1; sleep 2; "
          f"{x} mousemove {TASK_BOX[0]} {TASK_BOX[1]} click 1; sleep 0.5; "
          f"{x} type --delay 15 -- {shlex.quote(args.task)}; sleep 1; "
          f"{x} mousemove {SUBMIT[0]} {SUBMIT[1]} click 1")
    print("    Submitted. The agent's browser opens on the desktop; the UI shows each step.", flush=True)
    out = pc.wait_for(f"{HOME}/.venv/bin/python {HOME}/result.py {started}", "MARITIME_RESULT",
                      timeout_s=900, every_s=10, label="agent working")
    # Bring the Web UI back to the front so the screen ends on its answer.
    pc.sh(f"{x} search --name 'Browser Use WebUI' windowactivate 2>/dev/null; true", check=False)
    print("\n=== RESULT ===")
    print(out.split("MARITIME_RESULT", 1)[1].split("\n", 1)[1].strip())
    return 0 if "=== SUCCESS ===" in out else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
