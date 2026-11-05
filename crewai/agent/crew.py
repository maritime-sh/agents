"""A two-agent crewAI crew: a researcher finds one fact on the web, a writer
turns it into a short summary file. Runs inside the Maritime computer.

    python crew.py "When was the Python programming language first released?"

Model: any OpenAI-compatible endpoint. OPENAI_API_KEY, optional OPENAI_BASE_URL
(for example Maritime LLM, https://api.maritime.sh/api/llm/v1), CREWAI_MODEL
(default gpt-5.4).
"""

import logging
import os
import sys

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool

SUMMARY = "summary.md"  # written to the working folder, /data/agents/crewai/work
logging.getLogger("crewai.llms.base_llm").setLevel(logging.ERROR)  # quiet token-count notices


def build_llm() -> LLM:
    kwargs = {"model": "openai/" + os.environ.get("CREWAI_MODEL", "gpt-5.4")}
    if os.environ.get("OPENAI_BASE_URL"):
        kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
    return LLM(**kwargs)


def main(question: str) -> None:
    llm = build_llm()
    researcher = Agent(
        role="Web researcher",
        goal="Find a precise, sourced answer to the question on the live web",
        backstory=(
            "You check facts on real web pages. To search, read "
            "https://en.wikipedia.org/w/index.php?search=<your query> with the scrape tool, "
            "or open a reliable page you already know, and read the answer there."
        ),
        tools=[ScrapeWebsiteTool()],
        llm=llm,
        max_iter=8,
        verbose=True,
    )
    writer = Agent(
        role="Writer",
        goal="Turn research notes into a short, clear summary",
        backstory="You write three or four plain sentences and always name the source URL.",
        llm=llm,
        verbose=True,
    )
    research = Task(
        description=f"Answer this question using the web: {question}",
        expected_output="The answer, one supporting quote, and the source URL.",
        agent=researcher,
    )
    write = Task(
        description="Write a short Markdown summary of the research: a title, the answer, and the source.",
        expected_output="A Markdown summary of at most 80 words.",
        agent=writer,
        context=[research],
        output_file=SUMMARY,
    )
    crew = Crew(agents=[researcher, writer], tasks=[research, write], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    print("\n=== RESULT ===")
    print(str(result).strip())
    print(f"(saved to {os.path.abspath(SUMMARY)})")
    print("=== SUCCESS ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python crew.py "<question>"')
    main(" ".join(sys.argv[1:]))
