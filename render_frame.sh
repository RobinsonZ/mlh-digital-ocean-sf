#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <blend_file> <frame_number>"
    exit 1
fi

BLEND_FILE=$1
FRAME_NUMBER=$2
OUTPUT_FILE="${FRAME_NUMBER}.png"

if [ ! -f "$BLEND_FILE" ]; then
    echo "Error: Blend file '$BLEND_FILE' not found"
    exit 1
fi

TEMP_VIDEO="/tmp/frame_${FRAME_NUMBER}.mkv"

cat > /tmp/render_single_frame.py << EOF
import bpy
scene = bpy.context.scene
scene.frame_start = ${FRAME_NUMBER}
scene.frame_end = ${FRAME_NUMBER}
scene.render.filepath = "${TEMP_VIDEO}"
bpy.ops.render.render(animation=True)
EOF

blender --background "$BLEND_FILE" --python /tmp/render_single_frame.py > /dev/null 2>&1

ffmpeg -y -i "$TEMP_VIDEO" -vframes 1 "${OUTPUT_FILE}" > /dev/null 2>&1
rm -f "$TEMP_VIDEO"

echo "Rendered frame ${FRAME_NUMBER} to ${OUTPUT_FILE}"
