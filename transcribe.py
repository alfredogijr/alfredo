"""
Transcribes video audio with Whisper and exports word-level captions JSON.

Usage:
    python3 transcribe.py input.mp4 captions.json [--model base] [--lang pt]

Models (speed vs quality): tiny < base < small < medium < large
Default: base  (bom equilíbrio para redes sociais)
"""

import sys
import json
import argparse
import tempfile
from pathlib import Path

import whisper
from moviepy import VideoFileClip


WORDS_PER_CHUNK = 4   # quantas palavras por legenda


def extract_audio(video_path: str, out_wav: str):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(out_wav, logger=None)
    clip.close()


def transcribe(video_path: str, output_json: str, model_size: str, language: str):
    print(f"Carregando modelo Whisper '{model_size}'...")
    model = whisper.load_model(model_size)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_wav = tmp.name

    print("Extraindo áudio...")
    extract_audio(video_path, tmp_wav)

    print("Transcrevendo...")
    result = model.transcribe(tmp_wav, language=language, word_timestamps=True)
    Path(tmp_wav).unlink(missing_ok=True)

    captions = []
    for seg in result["segments"]:
        words = seg.get("words", [])
        if words:
            # Agrupa em chunks de WORDS_PER_CHUNK palavras
            for i in range(0, len(words), WORDS_PER_CHUNK):
                chunk = words[i : i + WORDS_PER_CHUNK]
                captions.append({
                    "start": chunk[0]["start"],
                    "end":   chunk[-1]["end"],
                    "text":  " ".join(w["word"].strip() for w in chunk),
                    "words": [
                        {"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
                        for w in chunk
                    ],
                })
        else:
            # Fallback sem timestamps de palavra
            tokens = seg["text"].split()
            dur_pw = (seg["end"] - seg["start"]) / max(1, len(tokens))
            for i in range(0, len(tokens), WORDS_PER_CHUNK):
                chunk_tokens = tokens[i : i + WORDS_PER_CHUNK]
                t0 = seg["start"] + i * dur_pw
                t1 = min(seg["end"], t0 + len(chunk_tokens) * dur_pw)
                captions.append({
                    "start": t0, "end": t1,
                    "text": " ".join(chunk_tokens), "words": [],
                })

    Path(output_json).write_text(
        json.dumps(captions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(captions)} chunks → {output_json}")
    for c in captions[:6]:
        print(f"  [{c['start']:.1f}–{c['end']:.1f}] {c['text']}")
    if len(captions) > 6:
        print("  ...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("output_json")
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang",  default="pt")
    args = parser.parse_args()
    transcribe(args.video, args.output_json, args.model, args.lang)
