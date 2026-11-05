# Tested: codex

All runs on 2026-11-04, on a Maritime account on the Growth plan, with `MARITIME_API_KEY` set and no model key (Maritime LLM injected by the template). Every reply below is the agent's real output.

- Image: `ghcr.io/maritime-sh/codex-agent@sha256:93aaaa891f8f04f4e68b39adc42a8c322da3292ffefadb3b622c794ce1c8288f`, the one Maritime's template pins. `codex --version` inside the agent: `codex-cli 0.154.0`.
- Steps: `deploy.py` created the agent from the template, polled until `active`, sent the task to chat and printed the reply. Later runs reused the agent by name.

## Runs

- `python3 deploy.py "Write primes.py that prints the first 10 prime numbers, run it, and show me the output."`
  Created `lib-codex`, active after 116 s, answered in 11 s with 2 to 29 (correct). `/data/workspace/primes.py` exists. This run is `demo.gif`.
- `python3 deploy.py "Change primes.py to take the count as a command line argument, run it with 15, and show me the output."`
  Reused the agent and the same file, answered in 15 s with the first 15 primes, 2 to 47 (correct).

## Notes

- No turn outlasted the chat request, so the receipt polling path in `deploy.py` (`X-Maritime-Chat-Result: turns-v1`, then `GET /chat/turns/{id}`) was not exercised in these runs.
- Nothing failed. The GIF is the real terminal output of the first run, rendered with `common/terminal_frames.py` and `common/make_gif.py`.
