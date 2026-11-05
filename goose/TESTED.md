# goose: test log

2026-11-04 (computer clock 2026-11-05 UTC), Maritime account on the Growth plan, model Maritime LLM (`gpt-5.4` through `https://api.maritime.sh/api/llm/v1`). Fresh Linux desktop.

| Command | Task | Result |
|---|---|---|
| `python3 deploy.py --install-only` | install | goose `1.57.0` installed in seconds |
| `python3 deploy.py "Use curl to read https://maritime.sh/pricing and tell me what the Growth plan costs a month and how many machines it keeps awake at once."` | web page via curl | 4 shell steps, answer "$100/month and keeps 25 machines awake at once" (correct). The page is a large HTML page, so most of the terminal output is raw HTML |
| `python3 deploy.py "Use the Hacker News API (https://hacker-news.firebaseio.com/v0/) to find the current top story. Tell me its title, score and number of comments."` | API, run 3 times | 1 shell step each time, correct title, score and comment count (checked against the API) |
| `python3 deploy.py "Use the Hacker News API (https://hacker-news.firebaseio.com/v0/) to get the current top 3 stories. Save their titles, scores and links to top3.md, then show me the file."` | API + file | 1 shell step, `top3.md` written in `/data/agents/goose/work` |
| `python3 deploy.py "Fetch https://pypi.org/pypi/requests/json, save the latest version and release date to latest.md, and show the file."` | API + file | 1 shell step, `latest.md` written: requests 2.34.2, released 2026-05-14 (correct, checked against PyPI). This run is `demo.gif` |

What went wrong and was fixed:
- The first install failed: the desktop has no `bzip2`, so the script now downloads the `.tar.gz` release asset (SHA-256 checked) instead of `.tar.bz2`.
- Terminal windows from earlier runs stayed open; each run now closes its previous goose terminal.
- The terminal view leaves out goose's ASCII mascot from its start banner (no upstream logos in images).
