"""Runs one mobile-use task on an Android phone that adb can already see.

Runs on your machine (deploy.py starts it with uv). mobile-use reads the phone's
screen and UI tree over adb, plans, and taps, swipes and types until the goal is done.

    python run.py --device 127.0.0.1:5555 "Open the Clock app and add an alarm for 7:30"

Model: any OpenAI-compatible endpoint (OPENAI_API_KEY, optional OPENAI_BASE_URL).
  MOBILE_USE_MODEL       the main model (default gpt-5.4): planner, cortex, orchestrator
  MOBILE_USE_FAST_MODEL  the small model (default gpt-5-mini): executor, contextor, utils
"""

import argparse
import asyncio
import os
import sys

from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform


def llm_config() -> LLMConfig:
    main = os.environ.get("MOBILE_USE_MODEL", "gpt-5.4")
    fast = os.environ.get("MOBILE_USE_FAST_MODEL", "gpt-5-mini")

    def node(model: str, fallback: str) -> LLMWithFallback:
        return LLMWithFallback(provider="openai", model=model, fallback=LLM(provider="openai", model=fallback))

    return LLMConfig(
        planner=node(main, fast),
        orchestrator=node(main, fast),
        cortex=node(main, fast),
        executor=node(fast, main),
        contextor=node(fast, main),
        utils=LLMConfigUtils(outputter=node(fast, main), hopper=node(fast, main)),
    )


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("goal")
    parser.add_argument("--device", required=True, help="adb serial, e.g. 127.0.0.1:5555")
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for an OpenAI-compatible endpoint).")

    profile = AgentProfile(name="default", llm_config=llm_config())
    config = Builders.AgentConfig.with_default_profile(profile=profile).for_device(
        platform=DevicePlatform.ANDROID, device_id=args.device
    )
    agent = Agent(config=config.build())
    try:
        await agent.init(retry_count=5, retry_wait_seconds=3)
        result = await agent.run_task(goal=args.goal, name="maritime")
    finally:
        await agent.clean()
    print("\n=== RESULT ===")
    print(result if result is not None else "(no final answer)")
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
