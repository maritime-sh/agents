#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow==11.3.0"]
# ///
"""Render a real terminal run as PNG frames for common/make_gif.py.

    python3 deploy.py "..." | tee run.log
    uv run common/terminal_frames.py run.log frames/ --command 'python3 deploy.py "..."'
    uv run common/make_gif.py frames/ demo.gif --agent ... --computer micro-VM ...

Each frame shows the log up to one more line group, so the GIF replays the
output exactly as it was printed. Nothing is added except the prompt line.
"""

import argparse
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 800, 470
PAD = 18
BG = (250, 250, 249)
FG = (28, 28, 30)
DIM = (120, 120, 125)
PROMPT = (37, 99, 235)
TASK = (21, 128, 61)


def mono(size: int):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def colour(line: str):
    if line.startswith("$ "):
        return PROMPT
    if line.startswith("> "):
        return TASK
    if line.startswith("  ") and ("status:" in line or "..." in line) or line.startswith("(answered"):
        return DIM
    return FG


def render(lines: list[str], font, line_h: int, cols: int) -> Image.Image:
    rows_all: list[tuple[str, tuple]] = []
    for line in lines:
        fill = colour(line)
        for part in textwrap.wrap(line, cols, subsequent_indent="  ", break_long_words=True) or [""]:
            rows_all.append((part, fill))
    shown = rows_all[-((HEIGHT - 2 * PAD) // line_h):]
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    for i, (text, fill) in enumerate(shown):
        draw.text((PAD, PAD + i * line_h), text, font=font, fill=fill)
    return img


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("log")
    p.add_argument("out")
    p.add_argument("--command", required=True, help="the command exactly as it was run")
    p.add_argument("--size", type=int, default=14)
    a = p.parse_args()

    font = mono(a.size)
    line_h = a.size + 6
    cols = int((WIDTH - 2 * PAD) / font.getlength("m"))
    log = pathlib.Path(a.log).read_text().rstrip("\n").splitlines()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    # One step per printed line, except that a multi-line reply appears in two halves.
    steps: list[int] = []
    reply_start = next((i + 2 for i, line in enumerate(log) if line.startswith("> ")), len(log))
    for i in range(1, len(log) + 1):
        if i <= reply_start or i == len(log) or log[i - 1] == "" or i == (reply_start + len(log)) // 2:
            steps.append(i)
    frames = [[f"$ {a.command}"]] + [[f"$ {a.command}"] + log[:n] for n in steps]
    for index, lines in enumerate(frames):
        render(lines, font, line_h, cols).save(out / f"{index:03d}.png")
    print(f"{len(frames)} frames in {out}")


if __name__ == "__main__":
    main()
