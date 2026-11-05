# mobile-use: test log

## 2026-11-04

- Phone: a new Maritime Android phone (Android 15, x86_64), reached through the adb tunnel from a Mac.
- Model: Maritime LLM through `OPENAI_BASE_URL` (`gpt-5.4` for planner, orchestrator and cortex; `gpt-5-mini` for executor, contextor and utils).
- `python3 deploy.py --setup-only`: phone created, tunnel opened, `adb` saw the device.
- `python3 deploy.py "Open the Clock app and add an alarm for 7:30 AM."`: success. The agent opened Clock from the launcher, went to Alarm, added an alarm, first set 7:35, noticed and corrected it to 7:30, tapped OK, and confirmed the alarm list showed 7:30 AM switched on ("Alarm set for 6 hours and 54 minutes from now"). 12 executor tool calls, about 3 minutes. This run is `demo.gif`.

## What went wrong on the way

- With a plain `pip install minitap-mobile-use==4.0.0`, the resolver picked langgraph 1.2.19 and langgraph-prebuilt 1.1.1, and the first tool call crashed: `ToolNode._extract_state() missing 1 required positional argument: 'config'`. Fixed by holding every dependency to the versions in upstream's own `uv.lock` for v4.0.0 (`agent/constraints.txt`, langgraph 1.0.10). `uv run --with` ignored `UV_CONSTRAINT`, so `deploy.py` now makes a venv once with `uv pip install -c`.
- The packaged CLI (`mobile-use`) looks for its LLM config next to site-packages and asks a telemetry question on a TTY, so `agent/run.py` calls the SDK directly with an explicit config instead.
- The Clock app showed a "Clock notifications are blocked" banner and an "Allow notifications" dialog; the agent handled both.
