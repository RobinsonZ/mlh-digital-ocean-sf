import os
import subprocess
import sys

blend_file = os.path.abspath(sys.argv[1])
output_path = os.path.abspath(sys.argv[2])
frame_start = int(sys.argv[3])
frame_end = int(sys.argv[4])
temp_output = output_path + ".temp.mkv"

with open("/tmp/blender_render.py", "w") as f:
    f.write(f"""
import bpy
bpy.context.scene.frame_start = {frame_start}
bpy.context.scene.frame_end = {frame_end}
bpy.context.scene.render.filepath = "{temp_output}"
bpy.context.scene.frame_step = 8
bpy.ops.render.render(animation=True, write_still=False)
""")

subprocess.run(
    ["blender", "--background", blend_file, "--python", "/tmp/blender_render.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

probe = subprocess.run(
    [
        "ffprobe",
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        temp_output,
    ],
    capture_output=True,
    text=True,
)

num_frames = int(probe.stdout.strip())
duration = num_frames / 30.0

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-r",
        "30",
        "-i",
        temp_output,
        "-t",
        str(duration),
        "-c:v",
        "ffv1",
        "-level",
        "3",
        "-coder",
        "1",
        "-context",
        "1",
        "-g",
        "1",
        "-slices",
        "24",
        "-slicecrc",
        "1",
        "-c:a",
        "pcm_s16le",
        "-af",
        f"atrim=0:{duration}",
        "-fflags",
        "+genpts",
        output_path,
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

os.remove(temp_output)
