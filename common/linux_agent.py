"""The shared deploy flow for agents that run inside a Maritime Linux desktop.

1. get (or create) the desktop, 2. upload the agent folder and install it,
3. pass the model key, 4. run the task in the background and stream its log.
"""

from __future__ import annotations

import os
import pathlib
import shlex
import sys
import time

from maritime_computer import Computer, MaritimeError


def deploy(
    *,
    slug: str,
    computer_name: str,
    agent_dir: pathlib.Path,
    env_vars: tuple[str, ...],
    run_command: str | None,
    task: str | None,
) -> int:
    home = f"/data/agents/{slug}"

    print(f"1/4 Getting the Linux desktop '{computer_name}' ...", flush=True)
    pc = Computer.get_or_create(computer_name, os="linux")
    print(f"    computer {pc.id}")
    print(f"    watch live: {pc.watch_link()}", flush=True)

    print(f"2/4 Installing {slug} (the first run takes a few minutes) ...", flush=True)
    pc.sh(f"mkdir -p {home}")
    for path in sorted(agent_dir.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            pc.write_file(f"{home}/{path.name}", path.read_bytes())
    # The exit marker ends the wait as soon as the install stops, failed or not.
    pc.background(f"bash {home}/install.sh; echo MARITIME_INSTALL_EXIT $?", f"{home}/install.log")
    out = pc.wait_for(f"tail -n 20 {home}/install.log", "MARITIME_INSTALL_EXIT", label="installing")
    if "MARITIME_AGENT_READY" not in out:
        raise MaritimeError(f"the install failed. Last lines of {home}/install.log:\n{out.strip()}")
    print("    " + next(line for line in out.splitlines() if "MARITIME_AGENT_READY" in line).strip())
    if run_command is None:
        return 0

    print("3/4 Passing your model key (kept in /data, readable only by the desktop user) ...", flush=True)
    lines = "".join(f"export {v}={shlex.quote(os.environ[v])}\n" for v in env_vars if os.environ.get(v))
    pc.write_file(f"{home}/.env", lines)
    pc.sh(f"chmod 600 {home}/.env")

    print(f"4/4 Running: {task}", flush=True)
    log = f"{home}/run-{int(time.time())}.log"
    pc.background(
        f"cd {home} && . ./.env && export DISPLAY=:1 PATH={home}/bin:$PATH ANONYMIZED_TELEMETRY=false "
        f"&& {run_command} {shlex.quote(task or '')}; echo MARITIME_RUN_EXIT $?",
        log,
    )
    seen = 0
    while True:
        out = pc.sh(f"cat {log}", check=False)
        if len(out) > seen:
            sys.stdout.write(out[seen:])
            sys.stdout.flush()
            seen = len(out)
        if "MARITIME_RUN_EXIT" in out:
            return 0 if "=== SUCCESS ===" in out else 1
        time.sleep(5)
