import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Lyric:
    m: int
    s: int
    c: int
    text: str

    def frame(self, fps: int = 240) -> int:
        total_seconds = self.m * 60 + self.s + self.c / 100.0
        return int(total_seconds * fps) + 1


def parse_lrc_file(filepath: str) -> list[Lyric]:
    lyrics = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\[(\d+):(\d+)\.(\d+)\]\s*(.*)", line.strip())
            if match:
                lyric = Lyric(
                    m=int(match.group(1)),
                    s=int(match.group(2)),
                    c=int(match.group(3)),
                    text=match.group(4),
                )
                lyrics.append(lyric)
    lyrics.sort(key=lambda x: x.frame())
    return lyrics


if len(sys.argv) != 2:
    print("Usage: render_frames.py <blend_file>")
    sys.exit(1)

blend_file = sys.argv[1]

# Clean and recreate output directory
out_dir = "out"
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

lyrics = parse_lrc_file("songs/you_make_me_feel_remix.lrc")

for i, lyric in enumerate(lyrics):
    if not lyric.text:
        continue
    frame = lyric.frame()
    print(f"Rendering frame {frame} ({i + 1}/{len(lyrics)}): {lyric.text}")
    subprocess.run(
        ["python3", "render_frame.py", blend_file, str(frame), out_dir],
        check=True,
    )

print(f"Rendered {len(lyrics)} frames")
