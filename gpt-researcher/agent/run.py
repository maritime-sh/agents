"""Runs one GPT Researcher job and saves the report as Markdown.

Runs inside the computer. GPT Researcher plans sub-questions, searches the web,
reads the pages it finds, and writes a cited report.

    python run.py "What is the Model Context Protocol and who supports it?"

Model: any OpenAI-compatible endpoint (OPENAI_API_KEY, optional OPENAI_BASE_URL).
GPT Researcher's own settings come from the environment (see its docs):
FAST_LLM, SMART_LLM, STRATEGIC_LLM, EMBEDDING, RETRIEVER, TOTAL_WORDS.
"""

import asyncio
import datetime
import os
import pathlib
import re
import sys

# Defaults that work with one OpenAI-compatible key and no search API key.
os.environ.setdefault("RETRIEVER", "duckduckgo")
os.environ.setdefault("FAST_LLM", "openai:gpt-5-mini")
os.environ.setdefault("SMART_LLM", "openai:gpt-5.4")
os.environ.setdefault("STRATEGIC_LLM", "openai:gpt-5.4")
os.environ.setdefault("EMBEDDING", "openai:text-embedding-3-small")
os.environ.setdefault("TOTAL_WORDS", "500")

from gpt_researcher import GPTResearcher  # noqa: E402

REPORTS = pathlib.Path("/data/agents/gpt-researcher/reports")


async def main(query: str) -> None:
    researcher = GPTResearcher(query=query, report_type="research_report")
    await researcher.conduct_research()
    report = await researcher.write_report()
    REPORTS.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:60]
    path = REPORTS / f"{datetime.date.today()}-{slug}.md"
    path.write_text(report)
    print(f"\n=== REPORT === {path}")
    print(f"sources: {len(researcher.get_source_urls())}")
    print("=== SUCCESS ===" if report.strip() else "=== NOT FINISHED ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python run.py "<research question>"')
    asyncio.run(main(" ".join(sys.argv[1:])))
