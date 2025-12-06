# Blender Karaoke Animation Project Context

## 🔷 High-level Goal

We already have word-timed lyrics exported from Aegisub as JSON (via exporter.lua).
The next step is to use that JSON inside Blender to generate animation keyframes – i.e., a karaoke-style text animation synced to an audio track.

Think:
`audio.mp3 + lyrics.json → Blender scene where words/lines are animated over time.`

---

## 🧩 Current Pipeline (Working)

### 1. Timing Tool: Aegisub + exporter.lua

Lyrics are timed in Aegisub using `\k` karaoke tags.

Each line looks like:
```
Dialogue: 0,0:00:10.00,0:00:15.00,Default,,0,0,0,,{\k20}I {\k30}watch {\k25}the {\k40}sun
```

`\kN` = N centiseconds for that syllable/word, relative to line start.

### exporter.lua behavior

- Filename: `exporter.lua` (not export_karaoke_json.lua).
- It's an Aegisub Automation macro.
- It does NOT use karaskel – instead it manually parses `\k` tags from line.text.
- It produces a `lyrics.json` file with absolute timestamps (ms) for each line and each word.

---

## 📜 JSON Schema (from exporter.lua)

The output looks like:

```json
[
  {
    "line_index": 12,
    "start": 12345,           // ms from start of audio
    "end": 15670,             // ms from start of audio
    "text": "{\\k20}I {\\k30}watch {\\k25}the {\\k40}sun",
    "words": [
      { "start": 12345, "end": 12545, "text": "I" },
      { "start": 12545, "end": 12845, "text": "watch" },
      { "start": 12845, "end": 13095, "text": "the" },
      { "start": 13095, "end": 13500, "text": "sun" }
    ]
  },
  ...
]
```

### Invariants:

- `start`/`end` are absolute milliseconds from t=0 of the audio.
- `words` array is ordered by start.
- Line text may still contain raw ASS/`\k` tags; `words[*].text` is already clean.

---

## 🖥️ Preview / Verification Script (Python, outside Blender)

File: probably something like `preview_words.py` (or `words.py`).

- Plays the MP3 via ffplay.
- Loads lyrics.json.
- Converts ms → seconds.
- Logs:
  - Line start events: `12.345s — I watch the sun go down`
  - Word events, colored: `12.345s I`, `12.545s watch`, etc.

This is just for sanity-checking timing; it's working and doesn't need help unless we want to enhance it.

---

## 🎯 New Task: Blender Keyframes

We now want to turn `lyrics.json` into Blender keyframes, using the absolute ms timestamps to drive animation on text.

### Constraints / Facts

- We're running Blender with Python available (Text Editor / scripting or external script).
- We have:
  - an audio file (e.g. `song.mp3` or `song.wav`)
  - the corresponding `lyrics.json` from exporter.lua
- Blender timeline FPS is configurable (e.g. 24, 30, 60).
- Conversion formula is:
  ```python
  frame = round((time_ms / 1000.0) * fps)
  ```
- For each word, we want at least one keyframe at start (and possibly at end) controlling something like:
  - visibility / alpha,
  - material emission,
  - location/scale,
  - or character spacing, etc.
- We haven't hard-decided the exact animation style yet, so the script should be modular (easy to swap what property is keyed).

---

## 🧱 What To Build (First Pass)

A Blender Python script (e.g. `import_lyrics_to_blender.py`) that:

1. Asks for or hardcodes:
   - path to `lyrics.json`
   - reference to the audio file
2. Loads the JSON.
3. For each line/word, converts `start`/`end` ms → frame numbers.
4. Creates or updates one or more Text objects in the scene.
5. Inserts keyframes using `object.keyframe_insert(...)` at the appropriate frames.

### Simple behavior options:

- **One Text object per line:**
  - At `line start_frame`: the text object is made visible with the full line string.
- **Or one Text object that:**
  - updates its text at each word start and keyframes something (e.g. opacity).

We can refine the behavior later; initial focus is "JSON → frames → keyframes" working correctly.

---

## 🔒 Invariants To Preserve

1. Treat `start`/`end` as absolute ms from audio = t=0.
2. Don't re-interpret `\k` – the JSON is already normalized.
3. Always derive frame numbers via `fps` param, not a magic constant.
4. Keep the JSON parser tolerant (ignore extra fields, unknown lines, etc.).

---

## ✅ Implemented: Blender Script

**File:** `blender/import_lyrics_to_blender.py`

### Features:
- Loads `lyrics.json` with absolute ms timestamps
- Converts ms → frames using configurable FPS
- Creates text objects organized in a "Lyrics" collection
- 4 animation styles (easily extensible):
  - `line_visibility` - Simple show/hide per line
  - `word_scale` - Words pop/pulse when sung
  - `word_emission` - Words glow brighter when active
  - `word_color` - Words change color (gray → gold)
- Optionally imports audio to VSE sequencer
- Auto-sets scene duration based on lyrics
- Clears previous lyrics on re-run

### Usage:
1. Open in Blender's Text Editor
2. Edit `CONFIG` dict at top (json path, audio path, FPS, style)
3. Run Script (Alt+P)

### Config Options:
```python
CONFIG = {
    "lyrics_json": "/path/to/lyrics.json",
    "audio_file": "/path/to/song.mp3",
    "fps": 30,
    "animation_style": "word_scale",  # or line_visibility, word_emission, word_color
    "font_size": 1.0,
    "line_spacing": 1.5,
    "collection_name": "Lyrics",
}
```
