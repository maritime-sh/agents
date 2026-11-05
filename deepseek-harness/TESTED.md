# Tested: deepseek-harness

All runs on 2026-11-04, on a Maritime account on the Growth plan, with `MARITIME_API_KEY` set and no model key (Maritime LLM injected by the template). Every reply below is the agent's real output.

- Image: `ghcr.io/maritime-sh/dsh-agent:0.1.0-rc.7`, the one Maritime's template pins. `dsh --version` inside the agent: `0.1.0-rc.7`.
- Steps: `deploy.py` created the agent from the template, polled until `active`, sent the task to chat and printed the reply. Later runs reused the agent by name.

## Runs

- `python3 deploy.py "Write fib.js that prints the first 12 Fibonacci numbers, run it with node, and show me the output."`
  Created `lib-deepseek-harness`, active after 42 s, answered in 11 s with 0 to 89 (correct). `/data/workspace/fib.js` exists. This run is `demo.gif`.
- `python3 deploy.py "Run node --version and tell me the result."`
  Reused the agent, answered "v22.23.2" in 4 s.

## Notes

- No turn outlasted the chat request, so the receipt polling path in `deploy.py` (`X-Maritime-Chat-Result: turns-v1`, then `GET /chat/turns/{id}`) was not exercised in these runs.
- Nothing failed. The GIF is the real terminal output of the first run, rendered with `common/terminal_frames.py` and `common/make_gif.py`.
