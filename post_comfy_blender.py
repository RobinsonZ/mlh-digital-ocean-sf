import os
import sys

from util import parse_lrc_file

lyrics = parse_lrc_file("songs/you_make_me_feel_remix.lrc")
lyrics_with_text = [lyric for lyric in lyrics if lyric.text]

# get list of all PNGs in in dir
in_dir = "in"
images = sorted([f for f in os.listdir(in_dir) if f.endswith((".png"))])

# validate number of images
if len(images) != len(lyrics_with_text):
    print(
        f"Error: Found {len(images)} images but expected {len(lyrics_with_text)} lyrics"
    )
    sys.exit(1)

# Print what frames they correspond to
for i, (image, lyric) in enumerate(zip(images, lyrics_with_text)):
    frame = lyric.frame()
    print(f"{image} -> frame {frame}")
