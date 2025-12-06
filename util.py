import re
from dataclasses import dataclass


@dataclass
class Lyric:
    m: int
    s: int
    c: int
    text: str

    def frame(self, fps: int = 240) -> int:
        total_seconds = self.m * 60 + self.s + self.c / 100.0
        return int(total_seconds * fps) + 1


def parse_lrc_file(filepath: str) -> list[Lyric]:
    lyrics = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\[(\d+):(\d+)\.(\d+)\]\s*(.*)", line.strip())
            if match:
                lyric = Lyric(
                    m=int(match.group(1)),
                    s=int(match.group(2)),
                    c=int(match.group(3)),
                    text=match.group(4),
                )
                lyrics.append(lyric)
    lyrics.sort(key=lambda x: x.frame())
    return lyrics
