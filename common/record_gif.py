#!/usr/bin/env python3
"""Record a Maritime computer's screen while an agent works, then make a demo GIF.

    python3 record_gif.py <computer-id> out.gif --seconds 600 --target 30

Takes a screenshot every --every seconds until --seconds pass or you press
Ctrl-C, drops frames that did not change, and speeds the rest up so the GIF
lasts about --target seconds. Needs ffmpeg on PATH.
"""

import argparse
import hashlib
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from maritime_computer import Computer, MaritimeError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("computer_id")
    parser.add_argument("out")
    parser.add_argument("--seconds", type=int, default=600)
    parser.add_argument("--every", type=float, default=1.5)
    parser.add_argument("--target", type=float, default=30.0, help="GIF length in seconds")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--stop-file", help="stop when this local file exists")
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required")

    pc = Computer.by_id(args.computer_id)
    frames = pathlib.Path(tempfile.mkdtemp(prefix="maritime-gif-"))
    last_hash, count, start = None, 0, time.time()
    try:
        while time.time() - start < args.seconds:
            if args.stop_file and pathlib.Path(args.stop_file).exists():
                break
            try:
                png = pc.screenshot()
            except (MaritimeError, OSError):
                time.sleep(args.every)
                continue
            digest = hashlib.sha1(png).hexdigest()
            if digest != last_hash:
                (frames / f"{count:05d}.png").write_bytes(png)
                count += 1
                last_hash = digest
            time.sleep(args.every)
    except KeyboardInterrupt:
        pass
    if count == 0:
        sys.exit("no frames captured")

    fps = max(count / args.target, 0.5)
    palette = frames / "palette.png"
    scale = f"scale={args.width}:-1:flags=lanczos"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", f"{fps:.3f}", "-i", str(frames / "%05d.png"),
                    "-vf", f"{scale},palettegen=stats_mode=diff", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", f"{fps:.3f}", "-i", str(frames / "%05d.png"),
                    "-i", str(palette), "-lavfi", f"{scale}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5",
                    "-loop", "0", args.out], check=True)
    print(f"{args.out}: {count} frames, about {count / fps:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
