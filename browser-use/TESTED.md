# browser-use: test record

Date: 2026-11-04. Maritime account on the Growth plan. Model: Maritime LLM, `gpt-5.4` through the OpenAI-compatible endpoint `https://api.maritime.sh/api/llm/v1`.

## Runs

- `python3 deploy.py --install-only` on a new Linux desktop: installed `browser-use==0.13.14`.
- "Go to maritime.sh/pricing and tell me what the Growth plan costs a month and how many machines it keeps awake at once." Answer: $100 a month, 25 machines awake (correct). browser-use's own judge flagged it because the price came from page text rather than a visible screenshot; the answer is right.
- "Go to news.ycombinator.com, open the comments of the top story, and tell me the story's title and how many comments it has." 2 steps, correct, run twice.
- "Go to maritime.sh, open the Docs, find the page about Android phones, and tell me which Android version the phones run and their screen size." 3 steps, answer "Android 15, 720 x 1280" (correct). This run is `demo.gif`.
- The dashboard install path (download `agent/install.sh` and `agent/run.py` from this repository, run the install in the background) on a fresh Linux desktop: returned in 1.3 seconds, install finished, `import browser_use` works.

## What went wrong on the way

- Chromium showed a "You are using an unsupported command-line flag" bar from browser-use's default flags. `run.py` now passes `--test-type`, which hides it.
