# Contributing

Thanks for helping more agents run on real computers. Two kinds of help are most useful.

## Suggest or add an agent

1. Open an issue with the **New agent** template: the agent, its license, and the computer it needs (Linux desktop, Windows desktop, Android phone or agent box).
2. If you build it yourself, copy the closest folder (`browser-use/` for a Linux desktop, `mobilerun/` for an Android phone, `open-instinct/` for a hosted agent) and follow its shape.

A folder is ready when it:

- installs the **official upstream release at a pinned version**, unchanged (no forks, no patches);
- runs end to end on a fresh Maritime computer with **one command**;
- has a `demo.gif` of about 30 seconds made from a real run (`common/make_gif.py`);
- has a `README.md` with what it does, how to run it, the upstream version, the upstream license and copyright line, and the community-integration note;
- adds a line to `TESTING.md` with the date, the task and the result.

New Maritime accounts start with a 7-day free trial. Maritime LLM (an OpenAI-compatible endpoint) works with most agents here, so one Maritime key is often all you need.

## Fix something

Bug reports with the exact command, the folder and the output help most. Small pull requests are welcome; please keep each one to one agent or one fix.

## Style

Plain, short sentences. Python scripts use the standard library only, so they run with a plain `python3`. Keys are read from the environment and never written into the repository.
