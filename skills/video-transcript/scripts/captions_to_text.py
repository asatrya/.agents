#!/usr/bin/env python3
"""Convert SRT/VTT captions into a readable plain-text transcript."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


TIMESTAMP_LINE = re.compile(
    r"^\s*(?:(?:\d{2}:)?\d{2}:\d{2}[,.]\d{3}|\d{2}:\d{2}[,.]\d{3})\s+-->"
)
TAG = re.compile(r"<[^>]*>")
VTT_POSITIONING = re.compile(r"\{\\[^}]+\}")


def clean_caption_line(line: str) -> str:
    line = VTT_POSITIONING.sub("", line)
    line = TAG.sub("", line)
    line = html.unescape(line)
    return " ".join(line.split())


def convert(source: Path) -> list[str]:
    lines = source.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    result: list[str] = []
    in_metadata_block = False
    skip_next_index = False

    for raw in lines:
        line = raw.strip()
        upper = line.upper()

        if upper in {"WEBVTT", "STYLE", "REGION"}:
            in_metadata_block = upper != "WEBVTT"
            continue
        if upper == "NOTE":
            in_metadata_block = True
            continue
        if not line:
            in_metadata_block = False
            skip_next_index = False
            continue
        if in_metadata_block:
            continue
        if TIMESTAMP_LINE.match(line):
            skip_next_index = False
            continue
        if line.isdigit() and skip_next_index is False:
            skip_next_index = True
            continue

        cleaned = clean_caption_line(line)
        if not cleaned:
            continue
        if result and result[-1] == cleaned:
            continue
        result.append(cleaned)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.source.suffix.lower() not in {".srt", ".vtt"}:
        raise SystemExit("source must be an .srt or .vtt file")

    transcript = convert(args.source)
    if not transcript:
        raise SystemExit("caption file contained no readable text")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(transcript) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
