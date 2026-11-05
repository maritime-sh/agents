# browser-use Web UI: test log

## 2026-11-04

- Computers: Maritime Linux desktops (Debian 13, XFCE, Chromium).
- Model: the Web UI's default, OpenAI `gpt-4o`, through Maritime LLM (`OPENAI_BASE_URL`, written to the Web UI's `OPENAI_ENDPOINT`).
- `python3 deploy.py "Go to news.ycombinator.com and tell me the title of the top story and how many points it has."`: success in about 40 seconds; it read the current top story and its points correctly. Not used for the demo, since the answer changes every day.
- From a brand new computer, `python3 deploy.py "Go to maritime.sh/pricing and tell me what the Growth plan costs a month."`: installed (under a minute), started the UI, ran the task. Answer: "The Growth plan costs $100 per month on the Maritime pricing page." (correct).
- Same task again on the first computer, recorded: "The Growth plan costs $100 per month on maritime.sh/pricing." (correct). This run is `demo.gif` (the window title bar and taskbar are cropped out because they show the Web UI's favicon).

## What went wrong on the way

- Agent Zero was the other candidate. Skipped: its supported install is Docker, and GitHub reports its license as NOASSERTION (the file reads MIT, Copyright (c) 2025 Agent Zero, s.r.o).
- First task run: every step failed with `connect_over_cdp: getaddrinfo ENOTFOUND localhost`. The Maritime Linux desktop image ships an empty `/etc/hosts`, so `localhost` does not resolve, and browser-use 0.1.48 connects to its browser at `http://localhost:9242`. Fixed in `agent/start.sh` without root: the Web UI runs in a private mount namespace with its own `/etc/hosts` (`unshare -rm` to bind-mount it, then a nested user namespace back to the desktop user). Skipped automatically when `localhost` resolves. Worth fixing in the image.
- At normal zoom the task box is below the fold, so the UI window opens maximized at 0.67 zoom; `deploy.py` clicks fixed positions for that layout with `xdotool`.
- The Web UI's emoji tab icons render as empty boxes: the desktop has no emoji font.
- Each REST screenshot leaks one X connection on Linux desktops (see gpt-researcher/TESTED.md); recordings were kept short.
