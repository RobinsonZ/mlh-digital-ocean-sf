import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import bpy

from util import parse_lrc_file

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []

if len(args) != 1:
    print(
        "Usage: blender --background --python post_comfy_blender.py -- <lyrics_blend_file>"
    )
    sys.exit(1)

source_blend = args[0]
new_blend = "post_comfy.blend"

shutil.copy(source_blend, new_blend)
bpy.ops.wm.open_mainfile(filepath=new_blend)

lyrics = parse_lrc_file("songs/you_make_me_feel_remix.lrc")
lyrics_with_text = [lyric for lyric in lyrics if lyric.text]

in_dir = "in"
images = sorted([f for f in os.listdir(in_dir) if f.endswith((".png"))])

if len(images) != len(lyrics_with_text):
    print(
        f"Error: Found {len(images)} images but expected {len(lyrics_with_text)} lyrics"
    )
    sys.exit(1)

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720

if not scene.sequence_editor:
    scene.sequence_editor_create()

for i, (image, lyric) in enumerate(zip(images, lyrics_with_text)):
    frame_start = lyric.frame()
    if i < len(lyrics_with_text) - 1:
        frame_end = lyrics_with_text[i + 1].frame()
    else:
        frame_end = frame_start + (240 * 2)

    image_path = os.path.abspath(os.path.join(in_dir, image))
    strip = scene.sequence_editor.strips.new_image(
        name=f"lyric_{i}", filepath=image_path, channel=1, frame_start=frame_start
    )
    strip.frame_final_duration = frame_end - frame_start

scene.render.use_sequencer = True
scene.render.film_transparent = False
scene.sequencer_colorspace_settings.name = "sRGB"

bpy.ops.wm.save_mainfile()
