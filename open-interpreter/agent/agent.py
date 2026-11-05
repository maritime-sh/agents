"""One Open Interpreter task on this Maritime Linux desktop, run without prompts.

Runs inside the computer, in a terminal window on the desktop. Open Interpreter writes
and runs code (Python, shell) on this computer to finish the task; windows it opens
appear on the desktop (DISPLAY :1).

    python agent.py "Make a bar chart of ... and open it in Chromium"

Model: any OpenAI-compatible endpoint. OPENAI_API_KEY, optional OPENAI_BASE_URL,
INTERPRETER_MODEL (default gpt-5.4).
"""

import os
import sys

from interpreter import interpreter


def main(task: str) -> None:
    interpreter.llm.model = "openai/" + os.environ.get("INTERPRETER_MODEL", "gpt-5.4")
    interpreter.llm.api_key = os.environ["OPENAI_API_KEY"]
    if os.environ.get("OPENAI_BASE_URL"):
        interpreter.llm.api_base = os.environ["OPENAI_BASE_URL"]
    interpreter.llm.context_window = 128000
    interpreter.llm.max_tokens = 4096
    interpreter.auto_run = True  # runs the code it writes without asking: this computer is its own
    interpreter.disable_telemetry = True
    interpreter.custom_instructions = (
        "You are on a Debian Linux desktop with a screen (DISPLAY=:1). Chromium is /usr/bin/chromium. "
        "Start GUI apps in the background (with &) so they stay open. Work in /data/agents/open-interpreter/work. "
        "Plots you make are also shown in an image viewer automatically; that is not Chromium, so when a task "
        "says to open something in Chromium, run /usr/bin/chromium with it yourself."
    )
    os.makedirs("/data/agents/open-interpreter/work", exist_ok=True)
    os.chdir("/data/agents/open-interpreter/work")
    messages = interpreter.chat(task)
    answer = next((m.get("content") for m in reversed(messages)
                   if m.get("role") == "assistant" and m.get("type") == "message"), None)
    print("\n=== RESULT ===")
    print(answer or "(no final answer)")
    print("=== SUCCESS ===" if answer else "=== NOT FINISHED ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: python agent.py "<task>"')
    main(" ".join(sys.argv[1:]))
