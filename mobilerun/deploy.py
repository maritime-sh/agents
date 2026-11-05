#!/usr/bin/env python3
"""Run Mobilerun (formerly DroidRun) on a Maritime Android phone.

The phone is an Android 15 machine on Maritime. Mobilerun runs where you run
this script and reaches the phone through Maritime's adb tunnel, so it sees the
phone exactly like a USB device.

    export MARITIME_API_KEY=mk_...
    export GOOGLE_API_KEY=...        # or OPENAI_API_KEY, or ANTHROPIC_API_KEY
    python3 deploy.py "Open Settings and tell me the Android version"

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

MOBILERUN = "mobilerun[anthropic]==0.7.4"   # pinned upstream release (pypi.org/project/mobilerun)
PORTAL_VERSION = "0.7.28"                   # the Portal app version mobilerun 0.7.4 installs


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def model_flags() -> list[str]:
    model = os.environ.get("MOBILERUN_MODEL")
    if os.environ.get("GOOGLE_API_KEY"):
        return ["-p", "GoogleGenAI", "-m", model or "gemini-2.5-flash"]
    if os.environ.get("OPENAI_API_KEY"):
        flags = ["-p", "OpenAI", "-m", model or "gpt-5.4"]
        if os.environ.get("OPENAI_BASE_URL"):
            flags = ["-p", "OpenAILike", "-m", model or "gpt-5.4", "--api_base", os.environ["OPENAI_BASE_URL"]]
        return flags
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ["-p", "Anthropic", "-m", model or "claude-sonnet-5-5"]
    sys.exit("Set GOOGLE_API_KEY, OPENAI_API_KEY or ANTHROPIC_API_KEY for the model.")


def mobilerun(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ, MOBILERUN_TELEMETRY_ENABLED="false", ANONYMIZED_TELEMETRY="false")
    return subprocess.run(["uvx", "--python", "3.12", "--from", MOBILERUN, "mobilerun", *args],
                          env=env, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("task", nargs="?", default="Open the Settings app and tell me which Android version this phone runs.")
    parser.add_argument("--name", default="mobilerun-phone", help="phone name, reused on every run")
    parser.add_argument("--setup-only", action="store_true")
    parser.add_argument("--vision", action="store_true", help="also send screenshots to the model")
    args = parser.parse_args()

    for tool in ("uvx", "adb"):
        if not shutil.which(tool):
            sys.exit(f"'{tool}' is not on PATH. Install uv and Android platform-tools first.")
    flags = [] if args.setup_only else model_flags()

    print(f"1/4 Getting the Android phone '{args.name}' ...", flush=True)
    phone = Computer.get_or_create(args.name, os="android")
    print(f"    phone {phone.id}")
    print(f"    watch live: {phone.watch_link()}", flush=True)

    print("2/4 Opening the adb tunnel ...", flush=True)
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

        print("3/4 Installing the Mobilerun Portal on the phone (once) ...", flush=True)
        if mobilerun("ping", "-d", serial, check=False).returncode != 0:
            mobilerun("setup", "-d", serial, "-pv", PORTAL_VERSION)
            mobilerun("ping", "-d", serial)
        if args.setup_only:
            return 0

        print(f"4/4 Running: {args.task}", flush=True)
        extra = ["--vision"] if args.vision else []
        return mobilerun("run", args.task, "-d", serial, "--steps", "25", *flags, *extra, check=False).returncode
    finally:
        subprocess.run(["adb", "disconnect", serial], capture_output=True)
        tunnel.terminate()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MaritimeError as error:
        sys.exit(f"Maritime error: {error}")
