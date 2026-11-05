# Tested: hermes-agent

All runs on 2026-11-04, on a Maritime account on the Growth plan, with `MARITIME_API_KEY` set and no model key (Maritime LLM injected by the template). Every reply below is the agent's real output.

- Image: `nousresearch/hermes-agent:v2026.5.16`, the one Maritime's template pins. `hermes --version` inside the agent: `Hermes Agent v0.14.0 (2026.5.16)`.
- Steps: `deploy.py` created the agent from the template, polled until `active`, sent the task to chat and printed the reply. Later runs reused the agent by name.

## Runs

- `python3 deploy.py "Find the current top story on news.ycombinator.com and tell me its title and points."`
  Created `lib-hermes-agent`, active after 47 s, answered in 27 s with the story's title and points. Checked against the Hacker News API a minute later: same story, points within a few of the live count.
- `python3 deploy.py "Remember this for later: my favorite programming language is Rust."`
  Answered "Got it." in 7 s. Hermes wrote it to `/opt/data/memories/USER.md`.
- `python3 deploy.py "What is my favorite programming language?"`
  Answered "Rust." in 5 s.
- `python3 deploy.py "What is my favorite programming language?"` (after putting the agent to sleep)
  The script found the agent sleeping, the chat woke it, and it answered "Rust." in 10 s: memory survives sleep.
- `python3 deploy.py "Remember that my favorite language is Rust, then tell me three Rust project ideas in one line each."` (agent asleep)
  The chat woke the agent and it answered in 15 s with three one-line ideas: a TUI habit tracker with SQLite, a file indexer with fuzzy search, a URL shortener with Axum and PostgreSQL. This run is `demo.gif`.

## Notes

- No turn outlasted the chat request, so the receipt polling path in `deploy.py` (`X-Maritime-Chat-Result: turns-v1`, then `GET /chat/turns/{id}`) was not exercised in these runs.
- Inside the image the CLI is at `/opt/hermes/.venv/bin/hermes`, not on PATH for `exec`; the template's chat path is unaffected.
- Nothing failed. The GIF is the real terminal output of the first run, rendered with `common/terminal_frames.py` and `common/make_gif.py`.
