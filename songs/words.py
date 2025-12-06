#!/usr/bin/env python3
import re
import subprocess
import time

COLORS = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
RESET = "\033[0m"


def parse_lrc(path):
    events = []
    with open(path) as f:
        for line in f:
            match = re.match(r"\[(\d+):(\d+\.\d+)\]\s*(.+)", line.strip())
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3)
                time_sec = minutes * 60 + seconds
                events.append((time_sec, text))
    events.sort()
    return events


def play_section(wav_path, start, end):
    return subprocess.Popen(
        [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "quiet",
            "-ss",
            str(start),
            "-t",
            str(end - start),
            wav_path,
        ]
    )


def main():
    lrc = "you_make_me_feel_remix.lrc"
    wav = "you_make_me_feel_remix.wav"

    events = parse_lrc(lrc)
    start_time = events[0][0]
    end_time = events[-1][0] + 2

    proc = play_section(wav, start_time, end_time)
    t0 = time.monotonic()

    try:
        for i, (ts, text) in enumerate(events):
            while time.monotonic() - t0 < ts - start_time:
                time.sleep(0.01)
            color = COLORS[i % len(COLORS)]
            print(f"{ts:.2f}s  {color}{text}{RESET}")
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.terminate()


if __name__ == "__main__":
    main()
