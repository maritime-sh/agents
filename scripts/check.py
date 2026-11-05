#!/usr/bin/env python3
"""Repository checks run in CI and before every commit.

Every agent folder has a README, a demo GIF and a one-command deploy script;
Python compiles; shell scripts parse; no long dashes and no key-shaped strings.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {".git", ".github", "assets", "common", "scripts", "docs"}
KEY = re.compile(r"(mk_[A-Za-z0-9]{12,}|mllm_[A-Za-z0-9]{12,}|sk-ant-[A-Za-z0-9-]{12,}|sk-or-[A-Za-z0-9-]{12,}|sk-proj-[A-Za-z0-9-]{12,}|AIza[0-9A-Za-z_-]{30,})")
DASHES = re.compile("[" + chr(0x2013) + chr(0x2014) + "]")
TEXT = {".md", ".py", ".sh", ".ps1", ".yml", ".yaml", ".toml", ".json", ".html", ".svg", ".txt"}

errors: list[str] = []
for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP and not p.name.startswith(".")):
    for need in ("README.md", "demo.gif"):
        if not (folder / need).exists():
            errors.append(f"{folder.name}: missing {need}")
    if not any((folder / n).exists() for n in ("deploy.py", "deploy.sh")):
        errors.append(f"{folder.name}: missing deploy.py or deploy.sh")

for path in ROOT.rglob("*"):
    if ".git" in path.parts or not path.is_file() or path.suffix not in TEXT:
        continue
    text = path.read_text(errors="replace")
    rel = path.relative_to(ROOT)
    if DASHES.search(text):
        errors.append(f"{rel}: contains an en or em dash")
    if KEY.search(text):
        errors.append(f"{rel}: contains something that looks like a key")
    if path.suffix == ".py":
        try:
            compile(text, str(rel), "exec")
        except SyntaxError as error:
            errors.append(f"{rel}: {error}")
    if path.suffix == ".sh" and subprocess.run(["bash", "-n", str(path)]).returncode != 0:
        errors.append(f"{rel}: bash syntax error")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("all checks passed")
