#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow==11.3.0"]
# ///
"""Turn screenshots of an agent's run into a captioned demo GIF of about 30 seconds.

    uv run common/make_gif.py frames/ out.gif --agent "browser-use" \
        --task "Find the Growth plan price" --answer "$100 a month" [--width 800]

Frames are the PNGs in the folder, in name order. Repeated frames are dropped,
each distinct screen is held long enough to read, and the final answer is shown
at the end. The top band names the agent and the Maritime computer it runs on.
"""

import argparse
import hashlib
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

BAND = (10, 10, 10)
ACCENT = (59, 130, 246)
WHITE = (255, 255, 255)
MUTED = (170, 170, 170)


def font(size: int, bold: bool = False):
    names = (["Arial Bold.ttf", "DejaVuSans-Bold.ttf"] if bold else ["Arial.ttf", "DejaVuSans.ttf"])
    for name in names:
        for base in ("/System/Library/Fonts/Supplemental/", "/Library/Fonts/", "/usr/share/fonts/truetype/dejavu/"):
            try:
                return ImageFont.truetype(base + name, size)
            except OSError:
                continue
    return ImageFont.load_default()


def band(width: int, title: str, line: str, line_color=WHITE) -> Image.Image:
    lines = textwrap.wrap(line, width=max(30, width // 11))[:2]
    height = 52 + 24 * len(lines)
    img = Image.new("RGB", (width, height), BAND)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 5, height], fill=ACCENT)
    draw.text((18, 12), title, font=font(17, bold=True), fill=WHITE)
    for i, text in enumerate(lines):
        draw.text((18, 40 + 24 * i), text, font=font(17), fill=line_color)
    return img


def compose(shot: Image.Image, top: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (shot.width, shot.height + top.height), BAND)
    canvas.paste(top, (0, 0))
    canvas.paste(shot, (0, top.height))
    return canvas


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("frames")
    p.add_argument("out")
    p.add_argument("--agent", required=True)
    p.add_argument("--computer", default="Linux desktop")
    p.add_argument("--task", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--width", type=int, default=800)
    p.add_argument("--seconds", type=float, default=30)
    p.add_argument("--drop", default="", help="comma-separated frame file names to leave out (e.g. a splash screen)")
    a = p.parse_args()

    dropped = {n.strip() for n in a.drop.split(",") if n.strip()}
    paths = [q for q in sorted(pathlib.Path(a.frames).glob("*.png")) if q.name not in dropped]
    seen, shots = set(), []
    for path in paths:
        digest = hashlib.sha1(path.read_bytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        img = Image.open(path).convert("RGB")
        shots.append(img.resize((a.width, round(img.height * a.width / img.width)), Image.LANCZOS))
    if not shots:
        raise SystemExit("no frames")

    title = f"{a.agent} on a Maritime {a.computer}"
    working = band(a.width, title, "Task: " + a.task)
    done = band(a.width, title, "Answer: " + a.answer, line_color=(134, 239, 172))
    answer_ms = 5000
    per = max(600, int((a.seconds * 1000 - answer_ms) / len(shots)))
    frames = [compose(s, working) for s in shots] + [compose(shots[-1], done)]
    durations = [per] * len(shots) + [answer_ms]
    height = max(f.height for f in frames)
    frames = [f if f.height == height else compose(f, Image.new("RGB", (a.width, height - f.height), BAND)) for f in frames]
    frames = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    size = pathlib.Path(a.out).stat().st_size / 1e6
    print(f"{a.out}: {len(shots)} screens, {sum(durations) / 1000:.0f} s, {size:.1f} MB")


if __name__ == "__main__":
    main()
