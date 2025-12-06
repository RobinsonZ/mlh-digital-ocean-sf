import os
import shutil
import subprocess
import sys

from util import parse_lrc_file


def render_frames(blend_file):
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: render_frames.py <blend_file>")
        sys.exit(1)
    render_frames(sys.argv[1])
