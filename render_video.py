import os
import shutil
import subprocess
import sys
import tempfile

TIME_OFFSET_MS = -170

blend_file = os.path.abspath(sys.argv[1])
output_path = os.path.abspath(sys.argv[2])
frame_start = int(sys.argv[3])
frame_end = int(sys.argv[4])

temp_dir = tempfile.mkdtemp()
temp_output = os.path.join(temp_dir, "frame_")

with open("/tmp/blender_render.py", "w") as f:
    f.write(f"""
import bpy
bpy.context.scene.frame_start = {frame_start}
bpy.context.scene.frame_end = {frame_end}
bpy.context.scene.render.filepath = "{temp_output}"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.frame_step = 8
bpy.ops.render.render(animation=True, write_still=True)
""")

subprocess.run(
    ["blender", "--background", blend_file, "--python", "/tmp/blender_render.py"],
    check=True,
)

fps = 240 / 8
audio_start_seconds = frame_start / 240
num_video_frames = (frame_end - frame_start) // 8
video_duration = num_video_frames / fps

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-pattern_type",
        "glob",
        "-i",
        f"{temp_dir}/frame_*.png",
        "-ss",
        str(audio_start_seconds),
        "-t",
        str(video_duration),
        "-i",
        "songs/Clarity.mp3",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        output_path,
    ],
    check=True,
)

shutil.rmtree(temp_dir)
