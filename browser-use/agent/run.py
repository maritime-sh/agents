"""Runs one browser-use task on this Maritime Linux desktop.

Runs inside the computer. The browser opens on the desktop's screen (DISPLAY :1),
so you can watch it from the Maritime viewer and take over at any moment.

    python run.py "Find the price of the Growth plan on maritime.sh"

Model: the first key that is set wins.
  ANTHROPIC_API_KEY              -> Claude (BROWSER_USE_MODEL, default claude-sonnet-5-5)
  OPENAI_API_KEY [+ OPENAI_BASE_URL] -> any OpenAI-compatible endpoint, including
                                    Maritime LLM (BROWSER_USE_MODEL, default gpt-5.4)
  GOOGLE_API_KEY                 -> Gemini (BROWSER_USE_MODEL, default gemini-2.5-flash)
"""

import asyncio
import os
import sys

from browser_use import Agent, Browser


def pick_llm():
    model = os.environ.get("BROWSER_USE_MODEL")
    if os.environ.get("ANTHROPIC_API_KEY"):
        from browser_use import ChatAnthropic

        return ChatAnthropic(model=model or "claude-sonnet-5-5")
    if os.environ.get("OPENAI_API_KEY"):
        from browser_use import ChatOpenAI

        kwargs = {"model": model or "gpt-5.4"}
        if os.environ.get("OPENAI_BASE_URL"):
            kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
        return ChatOpenAI(**kwargs)
    if os.environ.get("GOOGLE_API_KEY"):
        from browser_use import ChatGoogle

        return ChatGoogle(model=model or "gemini-2.5-flash")
    sys.exit("Set ANTHROPIC_API_KEY, OPENAI_API_KEY or GOOGLE_API_KEY")


async def main(task: str) -> None:
    browser = Browser(
        executable_path="/usr/bin/chromium",
        headless=False,  # visible on the desktop, so a person can watch and take over
        user_data_dir="/data/agents/browser-use/profile",  # logins survive sleep and redeploys
        window_size={"width": 1280, "height": 760},
        window_position={"width": 0, "height": 0},
        keep_alive=False,
        args=["--test-type"],  # hides Chromium's "unsupported command-line flag" bar on screen
    )
    agent = Agent(task=task, llm=pick_llm(), browser=browser)
    history = await agent.run(max_steps=int(os.environ.get("BROWSER_USE_MAX_STEPS", "30")))
    print("\n=== RESULT ===")
    print(history.final_result() or "(no final answer)")
    print("=== SUCCESS ===" if history.is_successful() else "=== NOT FINISHED ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python run.py "<task>"')
    asyncio.run(main(" ".join(sys.argv[1:])))
