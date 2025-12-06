#!/bin/bash
blender --background --python lyrics_to_blender.py
python3 render_video.py lyrics_project.blend output.mkv 29893 37665
