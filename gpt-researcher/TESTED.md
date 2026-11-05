# GPT Researcher: test log

## 2026-11-04

- Computer: a new Maritime Linux desktop (Debian 13, XFCE, Python 3.13).
- Model: Maritime LLM through `OPENAI_BASE_URL` (`gpt-5.4` smart and strategic, `gpt-5-mini` fast, `text-embedding-3-small` embeddings). Search: DuckDuckGo (`ddgs`), no search key.
- `python3 deploy.py --install-only`: installed `gpt-researcher 0.16.1` into `/data` in under a minute.
- `python3 deploy.py "What is the Model Context Protocol and which AI companies support it?"`: success, a cited report from 12 sources, about 2.5 minutes. (An earlier run of the same question gave 10 sources.)
- `python3 deploy.py "Which open-source AI agent frameworks are most used in 2026, and what is each one good at?"`: success, a cited report from 7 sources in about 2.5 minutes. Its summary: LangGraph for serious production builds, CrewAI as the fast path to multi-agent systems, LangChain as a common entry point, LlamaIndex for retrieval, Semantic Kernel in Microsoft-heavy shops. The report opened in Mousepad on the desktop. This run is `demo.gif`.

## What went wrong on the way

- The first launch of the desktop terminal did nothing: `pkill -f mousepad` matched its own launcher command line and killed it. Now `pkill -x mousepad`.
- The second launch failed with `Maximum number of clients reached` / `cannot open display: :1`. Cause: every `GET /api/v1/computers/{id}/screenshot` leaves one X connection open on the Linux desktop (25 X fds on a fresh Xvnc, 31 after 6 screenshots), and a 10 minute recording at 1.5 s used up the X server's ~256 client slots. Sleep and wake did not clear it (the VM resumed from memory). Killing `Xvnc` as the desktop user let the desktop supervisor restart it. The demo recordings were then kept under 150 screenshots per Xvnc start. This is a Maritime platform bug, not a GPT Researcher one.
- GPT Researcher logs `Failed to import MCPRetriever: No module named 'langchain_mcp_adapters'` at start. Harmless: the MCP retriever is optional and not used.
- Mousepad has no word wrap setting reachable without `gsettings` (not installed), so long report lines run past the window edge.
