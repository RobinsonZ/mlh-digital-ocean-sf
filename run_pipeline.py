import subprocess
import sys

from process_frames import process_frames
from render_frames import render_frames

if len(sys.argv) not in [2, 3]:
    print("usage: run_pipeline.py <api_key> [parallelism]")
    sys.exit(1)

api_key = sys.argv[1]
parallelism = int(sys.argv[2]) if len(sys.argv) == 3 else 1

print("step 1: creating blender project")
subprocess.run(
    [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "--background",
        "--python",
        "lyrics_to_blender.py",
    ],
    check=True,
)

print("\nstep 2: rendering frames")
render_frames("lyrics_project.blend")

print("\nstep 3: processing frames through comfy api")
process_frames(api_key, parallelism)

print("\ndone 🤘")
