"""A tiny client for Maritime computers (Linux, Windows, Android).

Standard library only, so every deploy script runs with a plain `python3`.
Reads the key from MARITIME_API_KEY (a Computers key is enough).

    from maritime_computer import Computer
    pc = Computer.get_or_create("browser-use-demo", os="linux")
    print(pc.sh("uname -a"))
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("MARITIME_API_URL", "https://api.maritime.sh").rstrip("/")
EXEC_LIMIT_S = 30  # one exec call may run at most 30 seconds


class MaritimeError(RuntimeError):
    pass


def _key() -> str:
    key = os.environ.get("MARITIME_API_KEY") or os.environ.get("MARITIME_COMPUTERS_KEY")
    if not key:
        sys.exit(
            "Set MARITIME_API_KEY first. Create one at https://maritime.sh/settings/api-keys#computers"
        )
    return key


def _call(method: str, path: str, body=None, raw: bytes | None = None, timeout: float = 120):
    headers = {"Authorization": f"Bearer {_key()}"}
    data = None
    if raw is not None:
        data = raw
        headers["Content-Type"] = "application/octet-stream"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{API}{path}", data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
                if not payload:
                    return None
                try:
                    return json.loads(payload)
                except ValueError:
                    return payload
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:600]
            if error.code in (502, 503, 504) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise MaritimeError(f"{method} {path} -> {error.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise MaritimeError(f"{method} {path} failed: {error}") from None
    return None


class Computer:
    def __init__(self, data: dict):
        self.data = data
        self.id: str = data["id"]
        self.os: str = data.get("os", "linux")

    @classmethod
    def get_or_create(cls, name: str, os: str = "linux") -> "Computer":
        """Returns the computer for this name, creating it the first time.

        The name doubles as the end-user id, so running a deploy twice reuses
        the same computer (and everything already installed on it).
        """
        data = _call(
            "POST",
            "/api/v1/computers",
            {"name": name, "externalUserId": name, "os": os},
            timeout=900,
        )
        return cls(data)

    @classmethod
    def by_id(cls, computer_id: str) -> "Computer":
        return cls(_call("GET", f"/api/v1/computers/{computer_id}"))

    def wake(self) -> None:
        _call("POST", f"/api/v1/computers/{self.id}/wake", {}, timeout=900)

    def sh(self, command: str, timeout: int = EXEC_LIMIT_S, check: bool = True) -> str:
        """Runs a shell command (bash on Linux and Android, PowerShell on Windows).

        Returns stdout. With check, a non-zero exit raises MaritimeError.
        """
        marker = "__MARITIME_RC__"
        if self.os == "windows":
            wrapped = f"{command}\nWrite-Output \"{marker}$LASTEXITCODE\""
        else:
            wrapped = f"{command}\necho \"{marker}$?\""
        result = _call(
            "POST",
            f"/api/v1/computers/{self.id}/exec",
            {"command": wrapped, "timeoutS": min(timeout, EXEC_LIMIT_S)},
            timeout=timeout + 90,
        ) or {}
        out = result.get("stdout", "") or ""
        err = result.get("stderr", "") or ""
        rc = None
        if marker in out:
            out, _, tail = out.rpartition(marker)
            tail = tail.strip()
            rc = int(tail) if tail.lstrip("-").isdigit() else 0
        if check and rc not in (None, 0):
            raise MaritimeError(f"command failed (exit {rc}):\n{command}\n{err[-2000:]}{out[-2000:]}")
        return out

    def background(self, command: str, log: str) -> None:
        """Starts a long command that keeps running after the 30 s exec limit."""
        if self.os == "windows":
            script = command.replace("'", "''")
            self.sh(
                "Start-Process powershell -WindowStyle Hidden -ArgumentList "
                f"'-NoProfile','-ExecutionPolicy','Bypass','-Command','& {{ {script} }} *> \"{log}\"'"
            )
        else:
            quoted = command.replace("'", "'\"'\"'")
            self.sh(f"nohup bash -lc '{quoted}' > {log} 2>&1 < /dev/null &")

    def wait_for(self, check_command: str, expect: str, timeout_s: int = 1800, every_s: int = 10,
                 label: str = "") -> str:
        """Polls check_command until its output contains expect."""
        start = time.time()
        while True:
            out = self.sh(check_command, check=False)
            if expect in out:
                return out
            if time.time() - start > timeout_s:
                raise MaritimeError(f"timed out waiting for {label or expect}. Last output:\n{out[-2000:]}")
            if label:
                print(f"  ... {label} ({int(time.time() - start)} s)", flush=True)
            time.sleep(every_s)

    def write_file(self, path: str, content: bytes | str) -> None:
        if isinstance(content, str):
            content = content.encode()
        query = urllib.parse.urlencode({"path": path})
        _call("PUT", f"/api/v1/computers/{self.id}/files?{query}", raw=content, timeout=300)

    def read_file(self, path: str) -> bytes:
        query = urllib.parse.urlencode({"path": path})
        result = _call("GET", f"/api/v1/computers/{self.id}/files?{query}", timeout=300)
        if isinstance(result, (bytes, bytearray)):
            return bytes(result)
        return json.dumps(result).encode()

    def screenshot(self) -> bytes:
        return self.read_bytes(f"/api/v1/computers/{self.id}/screenshot")

    def read_bytes(self, path: str) -> bytes:
        request = urllib.request.Request(f"{API}{path}", headers={"Authorization": f"Bearer {_key()}"})
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()

    def action(self, **body) -> dict:
        return _call("POST", f"/api/v1/computers/{self.id}/actions", body, timeout=120) or {}

    def watch_link(self) -> str:
        """A view-only link to watch the screen live."""
        result = _call("POST", f"/api/v1/computers/{self.id}/viewer", {"mode": "watch"}) or {}
        return result.get("url") or result.get("viewerUrl") or json.dumps(result)


def env_or_exit(*names: str) -> dict[str, str]:
    """Returns the first set variable of each group "A|B", or exits with a clear message."""
    found: dict[str, str] = {}
    missing = []
    for group in names:
        options = group.split("|")
        value = next((os.environ[o] for o in options if os.environ.get(o)), None)
        if value is None:
            missing.append(" or ".join(options))
        else:
            found[options[0]] = value
    if missing:
        sys.exit("Missing environment variables: " + ", ".join(missing))
    return found
