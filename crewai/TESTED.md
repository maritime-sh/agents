# crewAI: test log

2026-11-04 (computer clock 2026-11-05 UTC), Maritime account on the Growth plan, model Maritime LLM (`gpt-5.4` through `https://api.maritime.sh/api/llm/v1`). Fresh Linux desktop.

| Command | Task | Result |
|---|---|---|
| `python3 deploy.py --install-only` | install | `crewai==1.15.34` and `crewai-tools==1.15.34` installed in about two minutes |
| `python3 deploy.py "When was the Python programming language first released?"` | 3 runs | Researcher read the Wikipedia article on Python, writer produced the summary. Answer every time: first released 20 February 1991, as Python 0.9.0, source Wikipedia (correct). The last run is `demo.gif` |

Result of the last run, `/data/agents/crewai/work/summary.md`: a title, "Python was first released on 20 February 1991", a quote from Wikipedia, and the source URL.

What went wrong and was fixed:
- Run 1: the researcher was told to search through DuckDuckGo's HTML page, which answered with a bot challenge. The agent went to Wikipedia on its own and still answered correctly. The crew now searches through Wikipedia's search page.
- Runs 1 and 2: `output_file` with an absolute path was written under the working folder as `data/agents/...`; the summary file is now `summary.md` in the working folder.
- crewAI logs a token-count notice for model names it does not know; `crew.py` hides that logger. The emoji icons in crewAI's panels show as boxes in the desktop terminal (no emoji font).
- The researcher prints the whole scraped page into the terminal, so the terminal scrolls a lot during research.
