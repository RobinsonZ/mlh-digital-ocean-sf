#!/bin/bash
blender --background --python lyrics_to_blender.py
python3 render_video.py ./post_comfy.blend output.mkv 14401 57361
