"""Prints the final answer of the newest Web UI run once it has finished.

Runs inside the computer: python result.py <started-after-epoch>
Prints MARITIME_RESULT and the answer when the run's history file appears.
"""

import glob
import json
import os
import sys

after = float(sys.argv[1])
files = [f for f in glob.glob("/data/agents/browser-use-web-ui/web-ui-3.0.0/tmp/agent_history/*/*.json")
         if os.path.getmtime(f) > after]
if files:
    history = json.load(open(max(files, key=os.path.getmtime)))["history"]
    results = [r for step in history for r in (step.get("result") or [])]
    done = [r for r in results if r.get("is_done")]
    final = done[-1] if done else (results[-1] if results else {})
    print("MARITIME_RESULT steps=%d" % len(history))
    print(final.get("extracted_content") or final.get("error") or "(no final answer)")
    print("=== SUCCESS ===" if done and final.get("success", True) is not False else "=== NOT FINISHED ===")
