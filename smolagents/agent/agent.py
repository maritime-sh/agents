"""One smolagents CodeAgent task with web search and a webpage reader.

Runs inside the computer, in a terminal window on the desktop.

    python agent.py "What is the latest release of the requests library on PyPI?"

Model: any OpenAI-compatible endpoint. OPENAI_API_KEY, optional OPENAI_BASE_URL,
SMOLAGENTS_MODEL (default gpt-5.4).
"""

import os
import sys

from smolagents import CodeAgent, OpenAIServerModel, VisitWebpageTool, WebSearchTool


def main(task: str) -> None:
    model = OpenAIServerModel(
        model_id=os.environ.get("SMOLAGENTS_MODEL", "gpt-5.4"),
        api_base=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ["OPENAI_API_KEY"],
    )
    agent = CodeAgent(
        tools=[WebSearchTool(), VisitWebpageTool()],
        model=model,
        max_steps=int(os.environ.get("SMOLAGENTS_MAX_STEPS", "8")),
    )
    answer = agent.run(task)
    print("\n=== RESULT ===")
    print(answer)
    print("=== SUCCESS ===" if answer not in (None, "") else "=== NOT FINISHED ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python agent.py "<task>"')
    main(" ".join(sys.argv[1:]))
