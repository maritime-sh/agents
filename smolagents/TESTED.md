# smolagents: test record

Date: 2026-11-04. Maritime account on the Growth plan. Model: Maritime LLM, `gpt-5.4` through the OpenAI-compatible endpoint `https://api.maritime.sh/api/llm/v1` (`OPENAI_API_KEY` + `OPENAI_BASE_URL`), via smolagents' `OpenAIServerModel`.

## Command

```bash
python3 deploy.py "What is the latest release of the requests library on PyPI, and when was it published?"
```

## Runs

- **Fresh computer, default task** (`python3 deploy.py`, new Linux desktop): installed `smolagents[toolkit,openai]==1.26.0`, ran the task, answer "The latest release of requests on PyPI is 2.34.2, published on May 14, 2026." 51 seconds end to end, install included. Correct (PyPI shows 2.34.2 uploaded 2026-05-14).
- **Same computer, three more runs** with the same task: all gave the same correct answer. The demo run took 2 steps (one `web_search`, then `final_answer`). This run is `demo.gif`.

## Steps the agent took

1. Step 1: wrote `web_search(query="PyPI requests latest release ...")` and printed the results.
2. Step 2: `final_answer(...)` with the version and date from the results.

## What went wrong on the way

- In one of four runs the model answered in plain text without a code block in step 2; smolagents reported the parsing error and the agent gave the right `final_answer` in step 3. Not a failure, but it costs one extra step.
