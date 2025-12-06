# mlh-digital-ocean-sf
Project for MLH + DigitalOcean SF Hackathon 2025-12-05

Blender-based time-synced lyric video generator with AI-powered visuals.

## How It Works

1. **Parse Lyrics**: Reads LRC file (time-synced lyrics format) with centisecond precision timestamps
2. **Generate Blender Scene**: Creates a Blender project with text objects for each lyric, keyframed to appear/disappear at the correct times
3. **Render Base Frames**: Renders each lyric as a PNG frame from Blender
4. **AI Enhancement**: Sends each frame to ComfyUI API which uses the text as a seed image and generates trippy, surreal visuals with the lyrics embedded
5. **Final Output**: AI-enhanced frames can be compiled into the final music video

The LRC format looks like:
```
[02:04.45] You'll be that girl, 
[02:05.78] you'll be that girl
```

Where `[MM:SS.cs]` is the timestamp in minutes:seconds.centiseconds.

## Setup

Requires an instantiation of this ComfyUI workflow:
https://www.runcomfy.com/comfyui-workflows/my-workflows?shared_workflow=223d541f-9fa4-20ef-115a-0675c94166dd

![ComfyUI](.assets/comfyui.png)

## Usage

### Quick Start (Recommended)

Run the entire pipeline:
```sh
python3 run_pipeline.py $COMFY_API [parallelism]
```

This runs all three steps in sequence. Optional `parallelism` parameter (defaults to 1) controls concurrent API requests for step 3.

### Individual Steps

#### 1. Generate Blender Project
```sh
blender --background --python lyrics_to_blender.py
```
Creates `lyrics_project.blend` with text objects for each lyric, keyframed to match timing.

#### 2. Render Frames
```sh
python3 render_frames.py lyrics_project.blend
```
Renders each lyric frame to `out/` directory as PNG files named by frame number.

#### 3. Process Through ComfyUI API
```sh
python3 process_frames.py $COMFY_API [parallelism]
```
Submits each frame from `out/` to the ComfyUI API, which generates AI-enhanced visuals and downloads to `in/`.
- Automatically skips already-generated images
- Ctrl-C cancels active API jobs
- Uses random seeds for variety

## Aegisub Export Workflow

We built tooling to export word timings from Aegisub (subtitle editor with karaoke timing features), but ended up not using it since manually writing LRC files was faster. Still documented here for fun:

1. **Time lyrics in Aegisub**: Use Aegisub's karaoke timing mode to create word-level `\k` tags
2. **Export to JSON**: Run the Lua plugin (`songs/exporter.lua`) to export timing data as JSON
3. **Convert to LRC**: Run `python3 songs/json_to_lrc.py lyrics.json > output.lrc`

The Lua plugin parses `\k` tags from Aegisub and exports absolute timestamps for each word. The Python script converts that JSON to LRC format.

## Files

- `util.py` - LRC file parser
- `lyrics_to_blender.py` - generates Blender project with keyframed text objects
- `render_frame.py` - renders single frame from blend file
- `render_frames.py` - batch renders all lyric frames
- `process_frames.py` - submits frames to ComfyUI API with threading support
- `run_pipeline.py` - runs all three steps
- `post_comfy_blender.py` - validates output and creates final blend (WIP)
- `render_video.py` - renders final video (WIP)
- `songs/exporter.lua` - Aegisub plugin for exporting karaoke timing to JSON
- `songs/json_to_lrc.py` - converts JSON timing data to LRC format
