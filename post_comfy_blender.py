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

edit_scene = bpy.data.scenes["Edit"]
lyrics_scene = bpy.data.scenes["3D Lyrics"]

edit_scene.render.resolution_x = 1280
edit_scene.render.resolution_y = 720

lyrics_scene.render.resolution_x = 1280
lyrics_scene.render.resolution_y = 720

edit_scene.render.use_sequencer = True

if not edit_scene.sequence_editor:
    edit_scene.sequence_editor_create()

first_frame = lyrics_with_text[0].frame()

for i, (image, lyric) in enumerate(zip(images, lyrics_with_text)):
    frame_start = lyric.frame()
    if i < len(lyrics_with_text) - 1:
        frame_end = lyrics_with_text[i + 1].frame()
    else:
        frame_end = frame_start + (240 * 2)

    image_path = os.path.abspath(os.path.join(in_dir, image))
    strip = edit_scene.sequence_editor.strips.new_image(
        name=f"lyric_{i}", filepath=image_path, channel=1, frame_start=frame_start
    )
    strip.frame_final_duration = frame_end - frame_start

lyrics_strip = edit_scene.sequence_editor.strips.new_scene(
    name="3D_Lyrics", scene=lyrics_scene, channel=3, frame_start=first_frame + 24
)
lyrics_strip.scene_input = "CAMERA"

bpy.context.window.scene = edit_scene

bpy.ops.wm.save_mainfile()
