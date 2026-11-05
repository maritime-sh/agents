# Open Interpreter: test record

Date: 2026-11-04. Maritime account on the Growth plan. Model: Maritime LLM, `gpt-5.4` through the OpenAI-compatible endpoint `https://api.maritime.sh/api/llm/v1` (`OPENAI_API_KEY` + `OPENAI_BASE_URL`), as `openai/gpt-5.4` in Open Interpreter.

## Command

```bash
python3 deploy.py "Make a bar chart of the eight planets by diameter with matplotlib, save it as planets.png, and open it in Chromium."
```

## Runs

- **Fresh computer, default task** (`python3 deploy.py`, new Linux desktop): installed `open-interpreter==0.4.3` with Python 3.12, wrote and ran a Python script that saved `planets.png`, then ran `/usr/bin/chromium .../planets.png &`. Answer: "Done, I created planets.png and opened it in Chromium." 91 seconds end to end, install included. Result: success.
- **Same computer, final run** (the demo run): same steps, chart saved and shown in Chromium on the desktop. This run is `demo.gif`.

## Steps the agent took

1. Wrote a plan (make the chart, open it in Chromium).
2. Ran a shell block: `python3 - <<'PY'` with matplotlib (Agg backend), saved `/data/agents/open-interpreter/work/planets.png`.
3. Ran `/usr/bin/chromium /data/agents/open-interpreter/work/planets.png &`.
4. Final answer.

## What went wrong on the way

- First run: `ModuleNotFoundError: No module named 'pkg_resources'` at import. Open Interpreter 0.4.3 imports `pkg_resources`, which newer setuptools removed. Fixed: `install.sh` adds `setuptools==80.9.0`.
- One run used `python3` from a shell block, which was the system Python without matplotlib; the script failed, and the model still reported success because an older `planets.png` was in the folder. Fixed: `session.sh` puts the agent's own environment (with matplotlib) first on PATH. Worth knowing: Open Interpreter's final answer is the model's claim, not a check.
- When the chart is made in its Python (Jupyter) runner, Open Interpreter shows the image in the desktop's image viewer and tells the model "Displayed on the user's machine"; in one run the model took that as having opened Chromium and skipped that step. Fixed with one line in the custom instructions: the viewer is not Chromium, run `/usr/bin/chromium` yourself. The image viewer on this desktop also shows a harmless "thumbnailer service" notice.
- The terminal transcript redraws code blocks as they stream, so the log `deploy.py` prints repeats lines; `run.sh` drops repeated lines from that log. The desktop shows the real terminal.
