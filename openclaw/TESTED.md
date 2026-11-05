# Tested: openclaw

All runs on 2026-11-04, on a Maritime account on the Growth plan, with `MARITIME_API_KEY` set and no model key (Maritime LLM injected by the template). Every reply below is the agent's real output.

- Image: `ghcr.io/openclaw/openclaw:2026.7.1`, the one Maritime's template pins. `openclaw --version` inside the agent: `OpenClaw 2026.7.1`.
- Steps: `deploy.py` created the agent from the template, polled until `active`, sent the task to chat and printed the reply. Later runs reused the agent by name.

## Runs

- `python3 deploy.py "Look up the latest stable Python release on python.org and tell me its version and release date."`
  Created `lib-openclaw`, active after 54 s, answered in 13 s: "Python 3.15.2, Release date: Oct. 25, 2026". Checked against python.org/downloads: correct. This run is `demo.gif`.
- `python3 deploy.py "What is 17 times 23? Reply with just the number."`
  Reused the agent, answered "391" in 7 s.

## Notes

- No turn outlasted the chat request, so the receipt polling path in `deploy.py` (`X-Maritime-Chat-Result: turns-v1`, then `GET /chat/turns/{id}`) was not exercised in these runs.
- Nothing failed. The GIF is the real terminal output of the first run, rendered with `common/terminal_frames.py` and `common/make_gif.py`.
