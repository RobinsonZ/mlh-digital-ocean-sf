import os
import shutil
import subprocess
import sys

if len(sys.argv) not in [3, 4]:
    print("Usage: render_frame.py <blend_file> <frame_number> [output_dir]")
    sys.exit(1)

blend_file = sys.argv[1]
frame_number = int(sys.argv[2])
output_dir = sys.argv[3] if len(sys.argv) == 4 else "."
output_file = os.path.join(output_dir, f"{frame_number}.png")

if os.path.exists(blend_file):
    blend_file = os.path.abspath(blend_file)

if not os.path.exists(blend_file):
    print(f"Error: Blend file '{blend_file}' not found")
    sys.exit(1)

# Use Blender's command-line render with format override
subprocess.run(
    [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "--background",
        blend_file,
        "-F",
        "PNG",
        "-o",
        "/tmp/frame",
        "-f",
        str(frame_number),
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Move from Blender's output to our desired filename
blender_output = f"/tmp/frame{frame_number}.png"
if os.path.exists(blender_output):
    shutil.move(blender_output, output_file)

print(f"Rendered frame {frame_number} to {output_file}")
