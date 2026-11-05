# Open Instinct: test record

Date: 2026-11-04. Maritime account on the Growth plan, deployed with `--maritime-llm` (Maritime LLM, `gpt-5.4`).

## Runs

- `./deploy.sh --name "Demo" --handle demo-instinct --maritime-llm`: built `2e5e71b`, created the agent from `ghcr.io/mariagorskikh/open-instinct-agent:sha-2e5e71b`. The first hello failed with 503 because the agent was still deploying; `deploy.sh` now waits until the agent is active (about 90 seconds). After that, hello answered in about 5 seconds.
- Over `instinct chat`: the Growth price on maritime.sh/pricing (correct, 15 seconds, using its desktop browser); the top Hacker News story (correct; it took longer than the 30 second chat budget, so it answered on the next message); the Scale plan price using only the desktop browser (correct, $500). The last run is `demo.gif`.
