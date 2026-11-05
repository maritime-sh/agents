#!/usr/bin/env python3
"""Run mobile-use on a Maritime Android phone.

The phone is an Android 15 machine on Maritime. mobile-use runs where you run
this script and reaches the phone through Maritime's adb tunnel, so it sees the
phone exactly like a USB device.

    export MARITIME_API_KEY=mk_...
    export OPENAI_API_KEY=...            # plus OPENAI_BASE_URL for any OpenAI-compatible endpoint
    python3 deploy.py "Open the Clock app and add an alarm for 7:30 AM"

Needs: uv (https://docs.astral.sh/uv/) and adb (Android platform-tools).
"""

import argparse
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from maritime_computer import Computer, MaritimeError  # noqa: E402

MOBILE_USE = "minitap-mobile-use==4.0.0"   # pinned upstream release (pypi.org/project/minitap-mobile-use)
VENV_DIR = pathlib.Path.home() / ".cache" / "maritime-agents" / "mobile-use-4.0.0"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def install_mobile_use() -> str:
    """Installs the pinned release once into a local venv; returns its python.

    Every dependency is held to the version upstream locked for this release
    (agent/constraints.txt, from mobile-use's own uv.lock), so later releases of
    langgraph and friends cannot break it.
    """
    venv = VENV_DIR / ".venv"
    python = venv / "bin" / "python"
    if not (VENV_DIR / "ready").exists():
        print("    installing mobile-use (once, about a minute) ...", flush=True)
        subprocess.run(["uv", "venv", "-q", "--python", "3.12", str(venv)], check=True)
        subprocess.run(["uv", "pip", "install", "-q", "--python", str(python),
                        "-c", str(HERE / "agent" / "constraints.txt"), MOBILE_USE], check=True)
        (VENV_DIR / "ready").write_text(MOBILE_USE)
    return str(python)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?", default="Open the Clock app and add an alarm for 7:30 AM.")
    parser.add_argument("--name", default="mobile-use-phone", help="phone name, reused on every run")
    parser.add_argument("--setup-only", action="store_true")
    args = parser.parse_args()

    for tool in ("uv", "adb"):
        if not shutil.which(tool):
            sys.exit(f"'{tool}' is not on PATH. Install uv and Android platform-tools first.")
    if not args.setup_only and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for an OpenAI-compatible endpoint).")

    print(f"1/3 Getting the Android phone '{args.name}' ...", flush=True)
    phone = Computer.get_or_create(args.name, os="android")
    print(f"    phone {phone.id}")
    print(f"    watch live: {phone.watch_link()}", flush=True)

    print("2/3 Opening the adb tunnel ...", flush=True)
    port = free_port()
    serial = f"127.0.0.1:{port}"
    env = dict(os.environ, MARITIME_COMPUTERS_KEY=os.environ.get("MARITIME_API_KEY", ""))
    tunnel = subprocess.Popen(
        ["uv", "run", "-q", "--with", "aiohttp==3.12.15", "python", str(HERE.parent / "common" / "adb_tunnel.py"),
         phone.id, "--port", str(port)],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        line = tunnel.stdout.readline()
        if "listening" not in line:
            sys.exit(f"tunnel did not start: {line}")
        for _ in range(10):
            out = subprocess.run(["adb", "connect", serial], capture_output=True, text=True).stdout
            if "connected" in out:
                break
            time.sleep(2)
        subprocess.run(["adb", "-s", serial, "wait-for-device"], check=True, timeout=120)
        print(f"    adb device {serial}")
        if args.setup_only:
            return 0

        print(f"3/3 Running: {args.task}", flush=True)
        python = install_mobile_use()
        run_env = dict(os.environ, MOBILE_USE_TELEMETRY_ENABLED="false", ANONYMIZED_TELEMETRY="false")
        return subprocess.run([python, str(HERE / "agent" / "run.py"), args.task, "--device", serial],
                              env=run_env, cwd=HERE / "agent").returncode
    finally:
        subprocess.run(["adb", "disconnect", serial], capture_output=True)
        tunnel.terminate()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
