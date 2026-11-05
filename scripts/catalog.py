#!/usr/bin/env python3
"""Builds the agent tables and the demo gallery in README.md from agents.json.

    python3 scripts/catalog.py          # rewrite README.md
    python3 scripts/catalog.py --check  # fail if README.md is out of date (CI)

Everything between the BADGES, CATALOG and GALLERY markers in README.md is generated.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = [
    ("linux", "Linux desktop", "Agents that use a screen and a browser on a persistent Linux desktop."),
    ("android", "Android phone", "Agents that use apps on an Android 15 phone in the cloud."),
    ("agent-box", "Agent box", "Agents that live in their own micro-VM with a disk that persists, awake when there is work."),
    ("hosted", "Hosted agent template", "Agents Maritime hosts from a template, with chat, triggers and channels."),
    ("windows", "Windows desktop", "Agents that use Windows software."),
]


def badge(agent: dict) -> str:
    return f"[`{agent['slug']}/`]({agent['slug']}/)"


def catalog(agents: list[dict]) -> str:
    out = []
    for key, title, blurb in GROUPS:
        rows = [a for a in agents if a["computer"] == key]
        if not rows:
            continue
        out.append(f"### {title}\n\n{blurb}\n")
        out.append("| Agent | What it does | Upstream | License | Folder |")
        out.append("|---|---|---|---|---|")
        for a in rows:
            upstream = f"[{a['upstream']}](https://github.com/{a['upstream']}) `{a['version']}`"
            out.append(f"| **{a['name']}** | {a['what']} | {upstream} | {a['license']} | {badge(a)} |")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def gallery(agents: list[dict]) -> str:
    shown = [a for a in agents if (ROOT / a["slug"] / "demo.gif").exists()]
    cells = []
    for a in shown:
        width = 180 if a["computer"] == "android" else 380
        cells.append(
            f'<td align="center" valign="top" width="33%"><a href="{a["slug"]}/"><img src="{a["slug"]}/demo.gif" '
            f'width="{width}" alt="{a["name"]} on a Maritime computer"></a><br><b>{a["name"]}</b><br>'
            f'<sub>{a["computer_label"]}</sub></td>'
        )
    rows = ["<tr>" + "".join(cells[i:i + 3]) + "</tr>" for i in range(0, len(cells), 3)]
    return "<table>\n" + "\n".join(rows) + "\n</table>\n"


def badges(count: int) -> str:
    items = [
        (f"https://img.shields.io/badge/agents-{count}-2563eb?style=flat-square", "Agents", "#the-agents"),
        ("https://img.shields.io/badge/license-MIT-0a0a0a?style=flat-square", "MIT license", "LICENSE"),
        ("https://img.shields.io/github/actions/workflow/status/maritime-sh/agents/check.yml?branch=main&style=flat-square&label=checks", "Checks", "https://github.com/maritime-sh/agents/actions/workflows/check.yml"),
        ("https://img.shields.io/badge/docs-maritime.sh-0a0a0a?style=flat-square", "Docs", "https://maritime.sh/docs"),
        ("https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white", "Discord", "https://discord.gg/wvPAvXNZqm"),
        ("https://img.shields.io/badge/follow-@maritime__sh-0a0a0a?style=flat-square&logo=x", "X", "https://x.com/maritime_sh"),
    ]
    links = " ".join(f'<a href="{href}"><img src="{src}" alt="{alt}"></a>' for src, alt, href in items)
    return f'<p align="center">{links}</p>\n'


def replace(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    head, _, rest = text.partition(start)
    _, _, tail = rest.partition(end)
    return f"{head}{start}\n{body}{end}{tail}"


def main() -> int:
    agents = json.loads((ROOT / "agents.json").read_text())["agents"]
    readme = (ROOT / "README.md").read_text()
    new = replace(readme, "CATALOG", catalog(agents))
    new = replace(new, "GALLERY", gallery(agents))
    new = replace(new, "BADGES", badges(len(agents)))
    if "--check" in sys.argv:
        if new != readme:
            print("README.md is out of date: run python3 scripts/catalog.py")
            return 1
        return 0
    (ROOT / "README.md").write_text(new)
    print(f"README.md: {len(agents)} agents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
