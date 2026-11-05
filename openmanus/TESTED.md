# OpenManus: test log

2026-11-04 (computer clock 2026-11-05 UTC), Maritime account on the Growth plan, model Maritime LLM (`gpt-5.4` through `https://api.maritime.sh/api/llm/v1`). Fresh Linux desktop.

| Command | Task | Result |
|---|---|---|
| `agent/install.sh` | install | about ten minutes; `.venv` is 1.8 GB on `/data` |
| `python3 deploy.py "Go to news.ycombinator.com in the browser and tell me the title of the top story."` | browser | 4 steps, correct title |
| `python3 deploy.py "Go to news.ycombinator.com in the browser, open the comments page of the top story, and tell me the story's title and how many comments it has."` | browser, 2 runs | Correct title and comment count (179) both times. The browser tool opened the comments page in a background tab, so the visible tab stayed on the front page; on the second run several of the agent's JavaScript snippets failed and it read the count from the front page instead |
| `python3 deploy.py "Go to news.ycombinator.com in the browser and tell me the titles of the top 3 stories."` | browser | 4 steps (first extraction had a JavaScript syntax error, the agent retried with a simpler query), correct top 3 titles |
| `python3 deploy.py "Open maritime.sh/pricing in the browser and tell me what the Growth plan costs a month."` | browser | 3 steps (open the page, read it, finish), answer "The Growth plan costs $100/month." (correct). This run is `demo.gif` |

What went wrong and was fixed:
- The first install ran out of disk: `browsergym` (in OpenManus's requirements) pulls in PyTorch with CUDA libraries, more than the 4.6 GB `/data` disk. The install now uses `uv pip install --torch-backend cpu`.
- OpenManus sends `max_tokens` and a temperature to models it does not list as reasoning models; `gpt-5.4` rejects `max_tokens`. `run_manus.py` adds the configured model to OpenManus's reasoning and multimodal model lists at start (no file changed).
- OpenManus refuses to start without an optional remote-sandbox section in `config.toml`; `run_manus.py` writes it empty.
- At this commit OpenManus starts its browser tool with an unpinned `uvx browser-use --cli-mcp`, which needs a running Chromium with remote debugging. `config/mcp.json` now points to a pinned `browser-use==0.13.14`, and `run.sh` starts the desktop's Chromium on port 9222 and passes `BU_CDP_URL`.
- The first install was started by uploading `agent/install.sh` directly (to watch the disk); every run after that went through `deploy.py`, which reruns the same install script (a no-op when installed).
