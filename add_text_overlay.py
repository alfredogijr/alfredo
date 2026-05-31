"""
Video text overlay script.
Adds timed text captions to a video — a few sentences per segment.

Usage:
    python3 add_text_overlay.py input.mp4 output.mp4

The TEXT_SEGMENTS list below defines what text appears and when.
Each entry: (start_seconds, end_seconds, "text line 1", "text line 2", ...)
"""

import sys
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip

# ── Configure your captions here ────────────────────────────────────────────
# Each tuple: (start_sec, end_sec, line1, line2, ...)
TEXT_SEGMENTS = [
    (0,  4,  "Olá, bem-vindo!",          "Veja o que preparamos pra você."),
    (4,  8,  "Este é o primeiro ponto.",  "Simples e direto."),
    (8,  12, "Agora o segundo ponto.",    "Aqui a coisa fica interessante."),
    (12, 16, "Terceiro ponto chave.",     "Lembre disso!"),
    (16, 20, "E por fim...",              "Obrigado por assistir!"),
]

FONT_SIZE   = 40        # px
TEXT_COLOR  = (255, 255, 255, 255)    # RGBA white
SHADOW_COLOR = (0, 0, 0, 180)        # semi-transparent black shadow
BOX_COLOR   = (0, 0, 0, 140)         # dark translucent background behind text
MARGIN_BOTTOM = 60     # px from bottom edge
MAX_LINE_WIDTH = 40    # chars before wrapping
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


def make_text_frame(base_frame: np.ndarray, lines: list[str], font: ImageFont.FreeTypeFont) -> np.ndarray:
    h, w = base_frame.shape[:2]
    img = Image.fromarray(base_frame).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Measure each line
    wrapped = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=MAX_LINE_WIDTH) or [""])

    line_h = font.size + 8
    total_text_h = line_h * len(wrapped)
    pad_x, pad_y = 20, 14

    # Find widest line for the background box
    max_w = max(draw.textlength(l, font=font) for l in wrapped) if wrapped else 0
    box_x = (w - max_w) / 2 - pad_x
    box_y = h - MARGIN_BOTTOM - total_text_h - pad_y
    box_x2 = box_x + max_w + 2 * pad_x
    box_y2 = box_y + total_text_h + 2 * pad_y

    draw.rounded_rectangle([box_x, box_y, box_x2, box_y2], radius=10, fill=BOX_COLOR)

    y = box_y + pad_y
    for line in wrapped:
        lw = draw.textlength(line, font=font)
        x = (w - lw) / 2
        # shadow
        draw.text((x + 2, y + 2), line, font=font, fill=SHADOW_COLOR)
        # text
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += line_h

    result = Image.alpha_composite(img, overlay).convert("RGB")
    return np.array(result)


def build_segment_lookup(segments):
    """Returns a list of (start, end, lines) sorted by start."""
    return sorted([(s, e, list(txt)) for s, e, *txt in segments], key=lambda x: x[0])


def process_video(input_path: str, output_path: str):
    clip = VideoFileClip(input_path)
    font = load_font(FONT_SIZE)
    segment_list = build_segment_lookup(TEXT_SEGMENTS)

    def add_text(get_frame, t):
        frame = get_frame(t)
        for start, end, lines in segment_list:
            if start <= t < end:
                return make_text_frame(frame, lines, font)
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
    clip.close()
    print(f"\nDone! Saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_text_overlay.py input.mp4 output.mp4")
        sys.exit(1)
    process_video(sys.argv[1], sys.argv[2])
