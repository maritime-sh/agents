# Aider: test record

Date: 2026-11-04. Maritime account on the Growth plan. Model: Maritime LLM, `gpt-5.4` through the OpenAI-compatible endpoint `https://api.maritime.sh/api/llm/v1` (`OPENAI_API_KEY` + `OPENAI_BASE_URL`).

## Command

```bash
python3 deploy.py "Write primes.py with a function is_prime(n), and test_primes.py with unittest cases for a few primes and non-primes."
```

## Runs

- **Fresh computer, default task** (`python3 deploy.py`, new Linux desktop): installed `aider-chat==0.86.2` with Python 3.12, ran the task, committed `05be1f0 feat: add prime checker and unit tests`, 3 tests pass. 68 seconds end to end, install included. Result: success.
- **Same computer, run again** (the demo run): Aider wrote both files in one model call, committed `ee1ff6e feat: add prime checker and unit tests`, ran the tests itself (`--auto-test`), and the follow-up `python3 -m unittest -v` passed 2 tests. This run is `demo.gif`.
- Two earlier runs on the same computer also wrote passing files and tests.

## Steps the agent took

1. Fresh git repo under `/data/projects/aider-<time>`.
2. One request to the model (whole-file edit format), files created.
3. Commit with a model-written message.
4. `python3 -m unittest -v` through `--auto-test`, then again by the session script, then `git log`.

## What went wrong on the way

- First run: `git` was not found inside the desktop terminal (its PATH is shorter than the exec PATH), so Aider ran with no repo and made no commit. Fixed: `run.sh` passes its PATH to the terminal and `session.sh` adds the desktop's git location.
- With `gpt-5.4`, Aider sometimes says it "can't run the tests in this chat" before the files are applied; `--auto-test` runs them anyway.
- The first terminal setting (`--hold`) left an "exited" bar on screen; replaced by keeping a shell open in the window.
