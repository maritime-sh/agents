# Tested: zeroclaw

All runs on 2026-11-04, on a Maritime account on the Growth plan, with `MARITIME_API_KEY` set and no model key (Maritime LLM injected by the template). Every reply below is the agent's real output.

- Image: `ghcr.io/zeroclaw-labs/zeroclaw:v0.8.5-debian`, the one Maritime's template pins. `zeroclaw --version` inside the agent: `zeroclaw 0.8.5`.
- Steps: `deploy.py` created the agent from the template, polled until `active`, sent the task to chat and printed the reply. Later runs reused the agent by name.

## Runs

- `python3 deploy.py "Write a haiku about micro-VMs to haiku.txt in your workspace, then run cat on the file and show me what it printed."`
  Created `lib-zeroclaw`, active after 115 s, answered in 6 s with a three-line haiku. Checked with exec: the file exists with that text. This run is `demo.gif`.
- `python3 deploy.py "Run uname -a and tell me what kernel you are on."`
  Reused the agent, answered in 7 s: Linux `6.1.188-maritime1`.

## Notes

- No turn outlasted the chat request, so the receipt polling path in `deploy.py` (`X-Maritime-Chat-Result: turns-v1`, then `GET /chat/turns/{id}`) was not exercised in these runs.
- ZeroClaw wrote the file to its per-agent workspace `/zeroclaw-data/.zeroclaw/agents/default/workspace/`, not to `ZEROCLAW_WORKSPACE` (`/zeroclaw-data/workspace`). The README only says files stay on the agent's disk.
- Nothing failed. The GIF is the real terminal output of the first run, rendered with `common/terminal_frames.py` and `common/make_gif.py`.
