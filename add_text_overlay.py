"""
Video text overlay — Meta Kart / Instagram Reels.
Effects: vignette, contrast boost, typewriter, slide-up, scale-fade.

Usage:
    python3 add_text_overlay.py output.mp4 input1.mp4 [input2.mp4 ...]
"""

import sys
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, concatenate_videoclips

# ── Caption definitions ───────────────────────────────────────────────────────
# position : "top" | "center" | "bottom"
# anim     : "fade" | "typewriter" | "slide_up" | "scale_fade"
TEXT_SEGMENTS = [
    dict(start=0,  end=4,
         main=["CAMPO GRANDE"], sub=["ParkShoppingCampoGrande"],
         position="center", anim="scale_fade"),

    dict(start=6,  end=11,
         main=["A melhor pista indoor", "da Zona Oeste do Rio"], sub=[],
         position="bottom", anim="typewriter"),

    dict(start=14, end=19,
         main=["Bateria de 15 minutos", "capacete incluso"], sub=[],
         position="bottom", anim="slide_up"),

    dict(start=22, end=27,
         main=["Seg a Sex a partir das 16h",
               "Sáb, Dom e feriados a partir das 15h"], sub=[],
         position="bottom", anim="typewriter"),

    dict(start=30, end=35,
         main=["Reservas pelo WhatsApp", "(21) 97338-5900"], sub=[],
         position="bottom", anim="fade"),

    dict(start=37, end=40,
         main=["META KART"], sub=["Indoor Karting"],
         position="center", anim="scale_fade"),
]

# Hook segments (center/top) get a bigger font
FONT_SIZE_HOOK    = 66
FONT_SIZE_CAPTION = 48
FONT_SIZE_SUB     = 32

TEXT_COLOR    = (255, 255, 255, 255)
SHADOW_COLOR  = (0,   0,   0,   210)
BOX_COLOR     = (0,   0,   0,   155)

MAX_LINE_WIDTH_HOOK    = 20
MAX_LINE_WIDTH_CAPTION = 28

ANIM_DURATION      = 0.45   # seconds for entrance
TYPE_CHARS_PER_SEC = 22     # typewriter speed (chars/s)
VIGNETTE_STRENGTH  = 0.55   # 0 = off, 1 = heavy
CONTRAST_FACTOR    = 1.12   # slight contrast boost
# ─────────────────────────────────────────────────────────────────────────────


_font_cache: dict = {}

def load_font(size: int) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    font = ImageFont.load_default()
    for path in candidates:
        try:
            font = ImageFont.truetype(path, size)
            break
        except OSError:
            pass
    _font_cache[size] = font
    return font


def build_vignette(h: int, w: int, strength: float) -> np.ndarray:
    Y = np.linspace(-1, 1, h)[:, np.newaxis]
    X = np.linspace(-1, 1, w)[np.newaxis, :]
    dist = np.sqrt(X**2 + Y**2) / np.sqrt(2)
    mask = 1.0 - np.clip(dist * strength, 0, 1)
    return mask[:, :, np.newaxis]  # (h, w, 1) for broadcast


def grade_frame(frame: np.ndarray, vignette: np.ndarray) -> np.ndarray:
    f = frame.astype(np.float32)
    # contrast boost around midpoint
    f = (f - 128) * CONTRAST_FACTOR + 128
    # vignette
    f = f * vignette
    return np.clip(f, 0, 255).astype(np.uint8)


def typewriter_slice(main_lines: list, sub_lines: list, elapsed: float):
    """Return partial lines revealed by typewriter timing."""
    all_lines = main_lines + (sub_lines if sub_lines else [])
    total_chars = sum(len(l) for l in all_lines)
    shown = min(total_chars, int(elapsed * TYPE_CHARS_PER_SEC))

    result_main, result_sub = [], []
    rem = shown
    for line in main_lines:
        if rem <= 0:
            break
        take = min(len(line), rem)
        result_main.append(line[:take])
        rem -= take
    if sub_lines:
        for line in sub_lines:
            if rem <= 0:
                break
            take = min(len(line), rem)
            result_sub.append(line[:take])
            rem -= take

    return result_main or [""], result_sub


def box_y_for_position(position: str, h: int, box_h: int) -> int:
    if position == "top":
        return int(h * 0.08)
    elif position == "center":
        return (h - box_h) // 2
    else:  # bottom — above Instagram Reels UI (safe zone ends ~78% height)
        return int(h * 0.78) - box_h


def render_overlay(
    w: int, h: int,
    main_lines: list, sub_lines: list,
    font_main: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
    position: str,
    alpha: float = 1.0,
    y_shift: int = 0,
) -> Image.Image:
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_lw = MAX_LINE_WIDTH_HOOK if position in ("center", "top") else MAX_LINE_WIDTH_CAPTION
    wrapped_main = []
    for line in main_lines:
        wrapped_main.extend(textwrap.wrap(line, width=max_lw) or [""])
    wrapped_sub = []
    for line in sub_lines:
        wrapped_sub.extend(textwrap.wrap(line, width=max_lw + 8) or [""])

    gap     = 10
    lh_main = font_main.size + 12
    lh_sub  = font_sub.size  + 8
    total_h = lh_main * len(wrapped_main)
    if wrapped_sub:
        total_h += gap + lh_sub * len(wrapped_sub)

    pad_x, pad_y = 30, 18

    mw_main = max((draw.textlength(l, font=font_main) for l in wrapped_main), default=0)
    mw_sub  = max((draw.textlength(l, font=font_sub)  for l in wrapped_sub),  default=0)
    max_w   = max(mw_main, mw_sub)

    box_w  = max_w + 2 * pad_x
    box_x  = (w - box_w) / 2
    box_y  = box_y_for_position(position, h, total_h + 2 * pad_y) + y_shift
    box_x2 = box_x + box_w
    box_y2 = box_y + total_h + 2 * pad_y

    draw.rounded_rectangle(
        [box_x, box_y, box_x2, box_y2], radius=14,
        fill=(*BOX_COLOR[:3], int(BOX_COLOR[3] * alpha)),
    )

    def put(text, x, y, font):
        draw.text((x + 2, y + 2), text, font=font,
                  fill=(*SHADOW_COLOR[:3], int(SHADOW_COLOR[3] * alpha)))
        draw.text((x,     y),     text, font=font,
                  fill=(*TEXT_COLOR[:3],   int(TEXT_COLOR[3]   * alpha)))

    y = box_y + pad_y
    for line in wrapped_main:
        lw = draw.textlength(line, font=font_main)
        put(line, (w - lw) / 2, y, font_main)
        y += lh_main
    if wrapped_sub:
        y += gap
        for line in wrapped_sub:
            lw = draw.textlength(line, font=font_sub)
            put(line, (w - lw) / 2, y, font_sub)
            y += lh_sub

    return overlay


def composite_scaled(base: Image.Image, overlay: Image.Image, scale: float) -> Image.Image:
    """Scale the overlay's bounding box around its center before compositing."""
    if scale >= 1.0:
        return Image.alpha_composite(base, overlay)
    bbox = overlay.getbbox()
    if not bbox:
        return base
    region = overlay.crop(bbox)
    rw, rh = region.size
    nw, nh = max(1, int(rw * scale)), max(1, int(rh * scale))
    scaled = region.resize((nw, nh), Image.LANCZOS)
    cx = (bbox[0] + bbox[2]) // 2
    cy = (bbox[1] + bbox[3]) // 2
    result = base.copy()
    result.paste(scaled, (cx - nw // 2, cy - nh // 2), scaled)
    return result


def process_frame(
    frame: np.ndarray, t: float,
    segments: list,
    font_hook: ImageFont.FreeTypeFont,
    font_cap: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
    vignette: np.ndarray,
) -> np.ndarray:
    arr = grade_frame(frame, vignette)

    for seg in segments:
        start, end = seg["start"], seg["end"]
        if not (start <= t < end):
            continue

        elapsed  = t - start
        position = seg["position"]
        anim     = seg["anim"]
        main_l   = seg["main"]
        sub_l    = seg["sub"]
        font_m   = font_hook if position in ("center", "top") else font_cap

        h, w = arr.shape[:2]
        a_dur = ANIM_DURATION

        if anim == "fade":
            alpha, y_shift, scale = min(1.0, elapsed / a_dur), 0, 1.0
            ml, sl = main_l, sub_l

        elif anim == "typewriter":
            alpha, y_shift, scale = 1.0, 0, 1.0
            ml, sl = typewriter_slice(main_l, sub_l, elapsed)

        elif anim == "slide_up":
            p     = min(1.0, elapsed / a_dur)
            ease  = 1 - (1 - p) ** 3          # cubic ease-out
            alpha = p
            y_shift = int(70 * (1 - ease))
            scale = 1.0
            ml, sl = main_l, sub_l

        elif anim == "scale_fade":
            p     = min(1.0, elapsed / a_dur)
            ease  = 1 - (1 - p) ** 2          # quadratic ease-out
            alpha = ease
            scale = 0.78 + 0.22 * ease
            y_shift = 0
            ml, sl = main_l, sub_l

        else:
            alpha, y_shift, scale = 1.0, 0, 1.0
            ml, sl = main_l, sub_l

        base    = Image.fromarray(arr).convert("RGBA")
        overlay = render_overlay(w, h, ml, sl, font_m, font_sub,
                                 position, alpha=alpha, y_shift=y_shift)

        if anim == "scale_fade" and scale < 1.0:
            result = composite_scaled(base, overlay, scale)
        else:
            result = Image.alpha_composite(base, overlay)

        arr = np.array(result.convert("RGB"))
        break

    return arr


def process_video(output_path: str, input_paths: list[str]):
    clips = [VideoFileClip(p) for p in input_paths]
    clip  = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]

    font_hook = load_font(FONT_SIZE_HOOK)
    font_cap  = load_font(FONT_SIZE_CAPTION)
    font_sub  = load_font(FONT_SIZE_SUB)

    h_px, w_px = clip.size[1], clip.size[0]
    vignette   = build_vignette(h_px, w_px, VIGNETTE_STRENGTH)

    def add_effects(get_frame, t):
        return process_frame(
            get_frame(t), t, TEXT_SEGMENTS,
            font_hook, font_cap, font_sub, vignette,
        )

    clip.transform(add_effects).write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger="bar",
    )
    for c in clips:
        c.close()
    print(f"\nDone! → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_text_overlay.py output.mp4 input1.mp4 [input2.mp4 ...]")
        sys.exit(1)
    process_video(sys.argv[1], sys.argv[2:])
