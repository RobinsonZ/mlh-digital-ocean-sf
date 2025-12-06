#!/bin/bash
set -e

if [ $# -lt 1 ]; then
    echo "usage: do_it_all.sh <comfy_api_key> [parallelism]"
    exit 1
fi

COMFY_API=$1
PARALLELISM=${2:-1}

echo "step 1-3: running pipeline (create blender project, render frames, process through comfy)"
python3 run_pipeline.py "$COMFY_API" "$PARALLELISM"

echo ""
echo "step 4: creating post-comfy blender file with overlaid scenes"
blender --background --python post_comfy_blender.py -- lyrics_project.blend

echo ""
echo "step 5: rendering final video"
python3 render_video.py post_comfy.blend output.mkv 14401 57361

echo ""
echo "done 🔥 video output: output.mkv"
