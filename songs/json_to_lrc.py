#!/usr/bin/env python3
import json
import sys


def ms_to_lrc_timestamp(ms):
    total_seconds = ms / 1000.0
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    centiseconds = int((total_seconds % 1) * 100)
    return f"[{minutes:02d}:{seconds:02d}.{centiseconds:02d}]"


if len(sys.argv) != 2:
    print("usage: json_to_lrc.py <input.json>")
    sys.exit(1)

with open(sys.argv[1]) as f:
    data = json.load(f)

for line in data:
    for word in line["words"]:
        timestamp = ms_to_lrc_timestamp(word["start"])
        text = word["text"]
        print(f"{timestamp} {text}")
    print()
