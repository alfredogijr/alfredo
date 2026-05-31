"""
Video text overlay — Meta Kart Campo Grande.
Concatenates multiple clips then burns timed captions with fade-in.

Usage:
    python3 add_text_overlay.py output.mp4 input1.mp4 [input2.mp4 ...]
"""

import sys
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, concatenate_videoclips

# ── Captions ────────────────────────────────────────────────────────────────
# Each entry: (start_sec, end_sec, [main lines], [subtitle lines])
TEXT_SEGMENTS = [
    (0,   4,  ["CAMPO GRANDE"],                                           ["ParkShoppingCampoGrande"]),
    (6,   11, ["A melhor pista indoor", "da Zona Oeste do Rio"],           []),
    (14,  19, ["Bateria de 15 minutos", "capacete incluso"],               []),
    (22,  27, ["Seg a Sex a partir das 16h",
               "Sáb, Dom e feriados a partir das 15h"],                   []),
    (30,  35, ["Reservas pelo WhatsApp", "(21) 97338-5900"],               []),
    (37,  40, ["META KART"],                                              ["Indoor Karting"]),
]

FONT_SIZE_MAIN  = 52
FONT_SIZE_SUB   = 34
TEXT_COLOR      = (255, 255, 255, 255)
SHADOW_COLOR    = (0,   0,   0,   190)
BOX_COLOR       = (0,   0,   0,   150)
MARGIN_BOTTOM   = 80
MAX_LINE_WIDTH  = 34
FADE_IN_SECS    = 0.4
# ────────────────────────────────────────────────────────────────────────────


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def make_text_frame(
    base_frame: np.ndarray,
    main_lines: list[str],
    sub_lines: list[str],
    font_main: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
    alpha: float = 1.0,
) -> np.ndarray:
    h, w = base_frame.shape[:2]
    img = Image.fromarray(base_frame).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    wrapped_main = []
    for line in main_lines:
        wrapped_main.extend(textwrap.wrap(line, width=MAX_LINE_WIDTH) or [""])
    wrapped_sub = []
    for line in sub_lines:
        wrapped_sub.extend(textwrap.wrap(line, width=MAX_LINE_WIDTH + 6) or [""])

    gap = 8
    line_h_main = font_main.size + 10
    line_h_sub  = font_sub.size + 8
    total_h = line_h_main * len(wrapped_main)
    if wrapped_sub:
        total_h += gap + line_h_sub * len(wrapped_sub)

    pad_x, pad_y = 26, 16

    all_w = [draw.textlength(l, font=font_main) for l in wrapped_main]
    all_w += [draw.textlength(l, font=font_sub)  for l in wrapped_sub]
    max_w = max(all_w) if all_w else 0

    box_x  = (w - max_w) / 2 - pad_x
    box_y  = h - MARGIN_BOTTOM - total_h - pad_y
    box_x2 = box_x + max_w + 2 * pad_x
    box_y2 = box_y + total_h + 2 * pad_y

    draw.rounded_rectangle(
        [box_x, box_y, box_x2, box_y2],
        radius=12,
        fill=(*BOX_COLOR[:3], int(BOX_COLOR[3] * alpha)),
    )

    def draw_line(text, x, y, font):
        draw.text((x + 2, y + 2), text, font=font,
                  fill=(*SHADOW_COLOR[:3], int(SHADOW_COLOR[3] * alpha)))
        draw.text((x,     y),     text, font=font,
                  fill=(*TEXT_COLOR[:3],   int(TEXT_COLOR[3]   * alpha)))

    y = box_y + pad_y
    for line in wrapped_main:
        lw = draw.textlength(line, font=font_main)
        draw_line(line, (w - lw) / 2, y, font_main)
        y += line_h_main

    if wrapped_sub:
        y += gap
        for line in wrapped_sub:
            lw = draw.textlength(line, font=font_sub)
            draw_line(line, (w - lw) / 2, y, font_sub)
            y += line_h_sub

    return np.array(Image.alpha_composite(img, overlay).convert("RGB"))


def process_video(output_path: str, input_paths: list[str]):
    clips = [VideoFileClip(p) for p in input_paths]
    clip  = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]

    font_main    = load_font(FONT_SIZE_MAIN)
    font_sub     = load_font(FONT_SIZE_SUB)
    segment_list = sorted(TEXT_SEGMENTS, key=lambda x: x[0])

    def add_text(get_frame, t):
        frame = get_frame(t)
        for start, end, main_lines, sub_lines in segment_list:
            if start <= t < end:
                a = min(1.0, (t - start) / FADE_IN_SECS) if FADE_IN_SECS > 0 else 1.0
                return make_text_frame(frame, main_lines, sub_lines, font_main, font_sub, a)
        return frame

    processed = clip.transform(add_text)
    processed.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger="bar",
    )
    for c in clips:
        c.close()
    print(f"\nDone! Saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_text_overlay.py output.mp4 input1.mp4 [input2.mp4 ...]")
        sys.exit(1)
    process_video(sys.argv[1], sys.argv[2:])
