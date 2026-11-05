#!/usr/bin/env python3
"""Attach local Android tools to a Maritime Android computer.

  export MARITIME_COMPUTERS_KEY=mk_...
  python3 adb_tunnel.py <computer-id> [--port 5555] [--api https://api.maritime.sh]
  adb connect 127.0.0.1:5555

The tool listens on a local TCP port and relays each connection to the ``adb``
tunnel of the computer (``WS /api/v1/computers/{id}/adb``). ``adb``, Appium,
Maestro and mobile-mcp then see the computer as a device on the network. The
key travels in the ``Authorization`` header and is read from the environment,
so it does not show in the process list. Needs: ``pip install aiohttp``.

The same relay works with websocat:
  websocat -b tcp-l:127.0.0.1:5555 wss://<api>/api/v1/computers/<id>/adb -H "Authorization: Bearer $MARITIME_COMPUTERS_KEY"
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from aiohttp import ClientSession, WSMsgType

DEFAULT_API = "https://api.maritime.sh"
DEFAULT_PORT = 5555
LOOPBACK = "127.0.0.1"
KEY_VARIABLE = "MARITIME_COMPUTERS_KEY"
READ_BYTES = 65536
EXIT_USAGE = 2


async def relay(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, url: str, key: str) -> None:
    """Relays one local TCP connection to the tunnel until one side closes."""
    async with ClientSession() as session:
        try:
            tunnel = await session.ws_connect(url, headers={"Authorization": f"Bearer {key}"}, max_msg_size=0)
        except Exception as error:  # noqa: BLE001 - report every connect failure the same way
            print(f"tunnel refused: {error}", file=sys.stderr, flush=True)
            writer.close()
            return

        async def tunnel_to_local() -> None:
            async for message in tunnel:
                if message.type == WSMsgType.BINARY:
                    writer.write(message.data)
                    await writer.drain()
            if tunnel.close_code not in (None, 1000):
                print(f"tunnel closed: code {tunnel.close_code}", file=sys.stderr, flush=True)
            writer.close()

        pump = asyncio.create_task(tunnel_to_local())
        try:
            while data := await reader.read(READ_BYTES):
                await tunnel.send_bytes(data)
        except (ConnectionError, OSError):
            pass
        finally:
            pump.cancel()
            await tunnel.close()
            writer.close()


async def main() -> int:
    """Runs the local listener until Ctrl-C. Returns a process exit code."""
    parser = argparse.ArgumentParser(description="Relay local adb connections to a Maritime Android computer.")
    parser.add_argument("computer_id")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--api", default=os.environ.get("MARITIME_API_URL", DEFAULT_API))
    arguments = parser.parse_args()
    key = os.environ.get(KEY_VARIABLE, "")
    if not key:
        print(f"{KEY_VARIABLE} is required", file=sys.stderr)
        return EXIT_USAGE
    base = arguments.api.rstrip("/").replace("https://", "wss://", 1).replace("http://", "ws://", 1)
    url = f"{base}/api/v1/computers/{arguments.computer_id}/adb"
    server = await asyncio.start_server(lambda r, w: relay(r, w, url, key), LOOPBACK, arguments.port)
    print(f"listening: adb connect {LOOPBACK}:{arguments.port}", flush=True)
    async with server:
        await server.serve_forever()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(0)
