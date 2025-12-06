#!/usr/bin/env python3
import json
import sys
import time
import subprocess
import shutil
import re
from pathlib import Path

# ANSI colors for word highlighting
COLORS = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
]
RESET = "\033[0m"


def strip_ass_tags(text: str) -> str:
    """Remove ASS override tags like {\k20} and {\bord3}."""
    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_events(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    events = []

    for line in data:
        line_start_ms = line.get("start") or 0
        text_raw = line.get("text") or ""
        text_clean = strip_ass_tags(text_raw)

        # Parse words
        words = []
        for w in line.get("words", []):
            # uses absolute timestamps already from your exporter
            words.append({
                "start": w["start"] / 1000.0,
                "end": w["end"] / 1000.0,
                "text": w["text"]
            })

        events.append({
            "line_index": line.get("line_index"),
            "line_start": line_start_ms / 1000.0,
            "line_text": text_clean,
            "words": words,
        })

    # sort by line start time
    events.sort(key=lambda e: e["line_start"])
    return events


def play_audio(mp3_path: Path):
    """Play with ffplay in the background."""
    if shutil.which("ffplay") is None:
        print("error: ffplay not found (install ffmpeg)", file=sys.stderr)
        sys.exit(1)

    return subprocess.Popen(
        [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "quiet",
            str(mp3_path),
        ]
    )


def preview(mp3_path: Path, json_path: Path, offset_sec=0.0):
    events = load_events(json_path)
    if not events:
        print("No events found in JSON.")
        return

    print(f"Loaded {len(events)} lines")
    print(f"Playing: {mp3_path}\n")

    proc = play_audio(mp3_path)
    t0 = time.monotonic()

    try:
        # Flatten word events into a single timeline list
        word_events = []
        line_events = []

        for e in events:
            line_events.append({
                "time": e["line_start"] + offset_sec,
                "line": e,
            })

            for i, w in enumerate(e["words"]):
                word_events.append({
                    "time": w["start"] + offset_sec,
                    "line": e,
                    "word": w,
                    "color": COLORS[i % len(COLORS)],
                })

        # Combine line + word events into one sorted timeline
        timeline = (
            [(ev["time"], "line", ev) for ev in line_events] +
            [(ev["time"], "word", ev) for ev in word_events]
        )
        timeline.sort(key=lambda x: x[0])

        # Play & emit events as time passes
        for ts, kind, ev in timeline:
            while True:
                now = time.monotonic() - t0
                dt = ts - now
                if dt <= 0:
                    break
                time.sleep(min(dt, 0.03))

            if kind == "line":
                print(f"\n{ev['time']:7.3f}s  —  {ev['line']['line_text']}")
            else:
                w = ev["word"]
                color = ev["color"]
                print(f"{ev['time']:7.3f}s       {color}{w['text']}{RESET}")

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(1)
            except subprocess.TimeoutExpired:
                proc.kill()


def main():
    if len(sys.argv) < 3:
        print("Usage: python preview_words.py song.mp3 lyrics.json [offset_sec]")
        sys.exit(1)

    mp3 = Path(sys.argv[1])
    jsonfile = Path(sys.argv[2])
    offset = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.0

    if not mp3.is_file():
        print(f"MP3 not found: {mp3}")
        sys.exit(1)
    if not jsonfile.is_file():
        print(f"JSON not found: {jsonfile}")
        sys.exit(1)

    preview(mp3, jsonfile, offset)


if __name__ == "__main__":
    main()
