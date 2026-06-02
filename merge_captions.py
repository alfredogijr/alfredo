"""
Merge caption JSONs from multiple clips into one, offsetting timestamps.

Usage:
    python3 merge_captions.py output.json clip1.json clip2.json [clip3.json ...]

You need to provide the duration of each clip (except the last) via --durations.
If --durations is not set, the script reads the original video files from a
briefing JSON to compute durations automatically.

Examples:
    python3 merge_captions.py captions.json briefing.json c1.json c2.json
    python3 merge_captions.py captions.json --durations 19.9 c1.json c2.json
"""

import sys
import json
import argparse
from pathlib import Path


def merge(output_path: str, caption_files: list, offsets: list):
    merged = []
    for cap_file, offset in zip(caption_files, offsets):
        caps = json.loads(Path(cap_file).read_text(encoding="utf-8"))
        for c in caps:
            merged.append({
                **c,
                "start": round(c["start"] + offset, 3),
                "end":   round(c["end"]   + offset, 3),
                "words": [
                    {**w, "start": round(w["start"] + offset, 3),
                          "end":   round(w["end"]   + offset, 3)}
                    for w in c.get("words", [])
                ],
            })

    merged.sort(key=lambda c: c["start"])
    Path(output_path).write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Merged {len(merged)} caption chunks → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("caption_files", nargs="+")
    parser.add_argument("--durations", nargs="+", type=float,
                        help="Duration of each clip in seconds (except last)")
    parser.add_argument("--briefing",
                        help="Briefing JSON to auto-read clip durations from 'inputs'")
    args = parser.parse_args()

    if args.durations:
        offsets = [0.0]
        for d in args.durations[:-1] if len(args.durations) >= len(args.caption_files) \
                else args.durations:
            offsets.append(offsets[-1] + d)
        offsets = offsets[:len(args.caption_files)]
    elif args.briefing:
        from moviepy import VideoFileClip
        briefing = json.loads(Path(args.briefing).read_text(encoding="utf-8"))
        offsets  = [0.0]
        for inp in briefing["inputs"][:-1]:
            c = VideoFileClip(inp)
            offsets.append(offsets[-1] + c.duration)
            c.close()
        offsets = offsets[:len(args.caption_files)]
    else:
        offsets = [0.0] * len(args.caption_files)
        print("Warning: no durations provided, all captions start at t=0")

    merge(args.output, args.caption_files, offsets)
