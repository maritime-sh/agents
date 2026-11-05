"""Runs one OpenManus task on this Maritime Linux desktop. Runs inside the computer.

    python run_manus.py "Go to news.ycombinator.com and tell me the top story"

Writes OpenManus's own config files (config/config.toml, config/mcp.json) from
environment variables, then starts the upstream Manus agent unchanged.

Model: any OpenAI-compatible endpoint. OPENAI_API_KEY, optional OPENAI_BASE_URL
(for example Maritime LLM, https://api.maritime.sh/api/llm/v1), OPENMANUS_MODEL
(default gpt-5.4).
"""

import asyncio
import json
import os
import pathlib
import sys

HOME = pathlib.Path("/data/agents/openmanus")
SRC = HOME / "src"
MODEL = os.environ.get("OPENMANUS_MODEL", "gpt-5.4")


def write_config() -> None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for another OpenAI-compatible endpoint).")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm = (f'model = {json.dumps(MODEL)}\nbase_url = {json.dumps(base)}\napi_key = {json.dumps(key)}\n'
           'max_tokens = 8192\ntemperature = 0.0\n')
    toml = f"[llm]\n{llm}\n[llm.vision]\n{llm}\n[mcp]\nserver_reference = \"app.mcp.server\"\n"
    # OpenManus refuses to start without this optional remote-sandbox section; it is not used here.
    toml += '[daytona]\ndaytona_api_key = ""\n'
    path = SRC / "config" / "config.toml"
    path.write_text(toml)
    path.chmod(0o600)
    # Point OpenManus's browser tool at the pinned browser-use install (instead of `uvx browser-use`).
    mcp = {"mcpServers": {"browser_use": {"type": "stdio", "command": str(HOME / "bu" / "bin" / "browser-use"),
                                          "args": ["--cli-mcp"]}}}
    (SRC / "config" / "mcp.json").write_text(json.dumps(mcp, indent=2))


async def run(task: str) -> None:
    from app import llm

    # OpenManus sends max_completion_tokens (not max_tokens) only to the models it lists as
    # reasoning models, and passes screenshots only to models it lists as multimodal.
    # Newer OpenAI models need both, so add the chosen model to those two lists.
    for names in (llm.REASONING_MODELS, llm.MULTIMODAL_MODELS):
        if MODEL not in names:
            names.append(MODEL)

    from app.agent.manus import Manus

    agent = await Manus.create()
    try:
        result = await agent.run(task)
        print("\n=== RESULT ===")
        print(result)
        print("=== SUCCESS ===")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python run_manus.py "<task>"')
    os.chdir(SRC)
    sys.path.insert(0, str(SRC))
    write_config()
    asyncio.run(run(" ".join(sys.argv[1:])))
