# Testing

Every agent is tested the way you would use it: its own one command, on a real Maritime computer. Each folder keeps its own test record with the exact command, the task, the agent's real answer and anything that went wrong on the way. Every demo GIF comes from one of those runs.

Last full pass: 2026-11-04. Model for every run: Maritime LLM (`gpt-5.4`, OpenAI-compatible), on a Maritime account on the Growth plan.

| Agent | Computer | Version | Test record |
|---|---|---|---|
| [browser-use](browser-use/) | Linux desktop | `0.13.14` | [browser-use/TESTED.md](browser-use/TESTED.md) |
| [browser-use Web UI](browser-use-web-ui/) | Linux desktop | `v3.0.0` | [browser-use-web-ui/TESTED.md](browser-use-web-ui/TESTED.md) |
| [OpenManus](openmanus/) | Linux desktop | `3309bf4` | [openmanus/TESTED.md](openmanus/TESTED.md) |
| [Open Interpreter](open-interpreter/) | Linux desktop | `0.4.3` | [open-interpreter/TESTED.md](open-interpreter/TESTED.md) |
| [Aider](aider/) | Linux desktop | `0.86.2` | [aider/TESTED.md](aider/TESTED.md) |
| [smolagents](smolagents/) | Linux desktop | `1.26.0` | [smolagents/TESTED.md](smolagents/TESTED.md) |
| [crewAI](crewai/) | Linux desktop | `1.15.34` | [crewai/TESTED.md](crewai/TESTED.md) |
| [goose](goose/) | Linux desktop | `v1.57.0` | [goose/TESTED.md](goose/TESTED.md) |
| [GPT Researcher](gpt-researcher/) | Linux desktop | `0.16.1` | [gpt-researcher/TESTED.md](gpt-researcher/TESTED.md) |
| [Mobilerun](mobilerun/) | Android phone | `0.7.4` | [mobilerun/TESTED.md](mobilerun/TESTED.md) |
| [mobile-use](mobile-use/) | Android phone | `4.0.0` | [mobile-use/TESTED.md](mobile-use/TESTED.md) |
| [Open Instinct](open-instinct/) | Agent box with a desktop | `2e5e71b` | [open-instinct/TESTED.md](open-instinct/TESTED.md) |
| [OpenClaw](openclaw/) | Hosted agent | `2026.7.1` | [openclaw/TESTED.md](openclaw/TESTED.md) |
| [Hermes Agent](hermes-agent/) | Hosted agent | `v2026.5.16` | [hermes-agent/TESTED.md](hermes-agent/TESTED.md) |
| [Codex](codex/) | Hosted agent | `0.154.0` | [codex/TESTED.md](codex/TESTED.md) |
| [DeepSeek Harness](deepseek-harness/) | Hosted agent | `0.1.0-rc.7` | [deepseek-harness/TESTED.md](deepseek-harness/TESTED.md) |
| [ZeroClaw](zeroclaw/) | Hosted agent | `v0.8.5` | [zeroclaw/TESTED.md](zeroclaw/TESTED.md) |

## How the GIFs are made

Screenshots of the computer during the run (`common/record_gif.py`), or the real terminal output for agents with no screen (`common/terminal_frames.py`), turned into a captioned GIF of about 30 seconds with `common/make_gif.py`. Startup screens that show an upstream logo, and screens that show internal build names, are left out.

## Run the checks

```bash
python3 scripts/check.py      # every folder has a README, a GIF and a deploy script; no keys in files
python3 scripts/catalog.py    # rebuild the README tables from agents.json
```
