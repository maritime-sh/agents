#!/usr/bin/env python3
"""Deploy Hermes Agent as a hosted agent on Maritime and give it a task.

    export MARITIME_API_KEY=mk_...
    python3 deploy.py "Remember that my favorite language is Rust, then tell me three Rust project ideas in one line each"

Creates the agent from Maritime's `hermes` template the first time (image
`nousresearch/hermes-agent:v2026.5.16`), waits until it is active, sends your task through chat and prints
the reply. Run it again with a new task and it talks to the same agent.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

API = os.environ.get("MARITIME_API_URL", "https://api.maritime.sh").rstrip("/")
TEMPLATE = "hermes"
IMAGE = "nousresearch/hermes-agent:v2026.5.16"
DEFAULT_NAME = "lib-hermes-agent"


class MaritimeError(RuntimeError):
    pass


def key() -> str:
    value = os.environ.get("MARITIME_API_KEY") or os.environ.get("MARITIME_TOKEN")
    if not value:
        sys.exit("Set MARITIME_API_KEY first. Create one at https://maritime.sh/settings/api-keys")
    return value


def call(method: str, path: str, body=None, headers=None, timeout: float = 120):
    """One REST call. Returns (status, parsed JSON or None)."""
    head = {"Authorization": f"Bearer {key()}", **(headers or {})}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        head["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{API}{path}", data=data, method=method, headers=head)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                return response.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:600]
            if error.code in (502, 503, 504) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise MaritimeError(f"{method} {path} -> {error.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise MaritimeError(f"{method} {path} failed: {error}") from None
    raise MaritimeError(f"{method} {path} failed")


def find_agent(name: str) -> dict | None:
    _, agents = call("GET", "/api/agents?limit=200")
    if isinstance(agents, dict):
        agents = agents.get("results") or agents.get("agents") or []
    return next((a for a in agents if a.get("name") == name), None)


def create_agent(name: str) -> dict:
    body = {"name": name, "templateId": TEMPLATE, "useMaritimeLlm": True}
    _, agent = call("POST", "/api/agents", body, timeout=300)
    return agent


def wait_active(agent_id: str, timeout_s: int = 900) -> dict:
    start = time.time()
    last = None
    while True:
        _, agent = call("GET", f"/api/agents/{agent_id}")
        status = agent.get("status")
        if status != last:
            print(f"  status: {status} ({int(time.time() - start)} s)", flush=True)
            last = status
        if status in ("active", "running", "sleeping"):
            return agent
        if status in ("error", "failed", "stopped"):
            raise MaritimeError(f"agent is {status}; see https://maritime.sh/agents/{agent_id}")
        if time.time() - start > timeout_s:
            raise MaritimeError(f"agent still {status} after {timeout_s} s")
        time.sleep(5)


def chat(agent_id: str, message: str, timeout_s: int = 600) -> str:
    """Sends one message. Long turns come back as a receipt that we poll."""
    headers = {"X-Maritime-Chat-Result": "turns-v1", "Idempotency-Key": str(uuid.uuid4())}
    status, result = call("POST", f"/api/agents/{agent_id}/chat", {"message": message},
                          headers=headers, timeout=timeout_s)
    start = time.time()
    while status == 202 or (result or {}).get("state") in ("accepted", "running"):
        delivery = result.get("deliveryId") or result.get("delivery_id")
        if time.time() - start > timeout_s:
            raise MaritimeError(f"no reply after {timeout_s} s (delivery {delivery})")
        print(f"  ... working ({int(time.time() - start)} s)", flush=True)
        time.sleep(5)
        status, result = call("GET", f"/api/agents/{agent_id}/chat/turns/{delivery}")
    if result.get("error") and not result.get("response"):
        raise MaritimeError(result["error"])
    return result.get("response") or ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("task", nargs="?", default="Remember that my favorite language is Rust, then tell me three Rust project ideas in one line each")
    parser.add_argument("--name", default=DEFAULT_NAME, help=f"agent name (default {DEFAULT_NAME})")
    args = parser.parse_args()

    agent = find_agent(args.name)
    if agent:
        print(f"Using agent {args.name} ({agent['id']})")
    else:
        print(f"Creating agent {args.name} from the {TEMPLATE} template ({IMAGE})")
        agent = create_agent(args.name)
    agent_id = agent["id"]
    wait_active(agent_id)
    print(f"Dashboard: https://maritime.sh/agents/{agent_id}")
    print(f"\n> {args.task}\n", flush=True)
    started = time.time()
    reply = chat(agent_id, args.task)
    print(reply.strip())
    print(f"\n(answered in {int(time.time() - started)} s)")


if __name__ == "__main__":
    try:
        main()
    except MaritimeError as error:
        sys.exit(f"error: {error}")
