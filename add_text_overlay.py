"""
Instagram Reels overlay engine.
Features: Ken Burns, progress bar, brand accent, typewriter, slide-up,
          scale-fade, fade-out, auto-captions with word highlight.

Usage:
    python3 add_text_overlay.py briefing.json output.mp4
    python3 add_text_overlay.py briefing.json output.mp4 override1.mp4 ...

Briefing JSON keys:
    inputs, brand_color, progress_bar, ken_burns, vignette, contrast,
    segments, disclaimer, disclaimer_start,
    captions_file   – path to captions JSON from transcribe.py
    captions_mode   – "always" | "fill_gaps" (default: fill_gaps)
    captions_y      – fraction of height for caption zone (default: 0.62)
"""

import sys
import json
import textwrap
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, concatenate_videoclips


def load_font(size: int, _cache: dict = {}) -> ImageFont.FreeTypeFont:
FONTS_DIR = Path(__file__).parent / "fonts"

# Font priority: Meta Kart brand fonts → system fallback
FONT_TITLE_CANDIDATES = [
    str(FONTS_DIR / "HKModular-Bold.ttf"),
    str(FONTS_DIR / "HKModular-Black.ttf"),
    str(FONTS_DIR / "BarlowCondensed-Black.ttf"),   # fallback
    str(FONTS_DIR / "BarlowCondensed-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_BODY_CANDIDATES = [
    str(FONTS_DIR / "Montserrat-Bold.ttf"),
    str(FONTS_DIR / "Montserrat-SemiBold.ttf"),
    str(FONTS_DIR / "BarlowCondensed-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def load_font(size: int, role: str = "body", _cache: dict = {}) -> ImageFont.FreeTypeFont:
    key = (size, role)
    if key not in _cache:
        candidates = FONT_TITLE_CANDIDATES if role == "title" else FONT_BODY_CANDIDATES
        font = ImageFont.load_default()
        for path in candidates:
            try:
                font = ImageFont.truetype(path, size)
                break
            except OSError:
                pass
        _cache[key] = font
    return _cache[key]


def build_vignette(h: int, w: int, strength: float) -> np.ndarray:
    Y = np.linspace(-1, 1, h)[:, None]
    X = np.linspace(-1, 1, w)[None, :]
    mask = 1.0 - np.clip(np.sqrt(X**2 + Y**2) / np.sqrt(2) * strength, 0, 1)
    return mask[:, :, None]


def grade_frame(frame: np.ndarray, vignette: np.ndarray, contrast: float) -> np.ndarray:
    f = (frame.astype(np.float32) - 128) * contrast + 128
    return np.clip(f * vignette, 0, 255).astype(np.uint8)


def apply_ken_burns(frame: np.ndarray, scale: float) -> np.ndarray:
    if abs(scale - 1.0) < 0.001:
        return frame
    h, w = frame.shape[:2]
    nh, nw = max(1, int(h / scale)), max(1, int(w / scale))
    y0, x0 = (h - nh) // 2, (w - nw) // 2
    cropped = frame[y0:y0 + nh, x0:x0 + nw]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))


def draw_progress_bar(frame: np.ndarray, t: float, total: float,
                      color: tuple, bar_h: int = 5) -> np.ndarray:
    arr = frame.copy()
    bar_w = max(0, int(arr.shape[1] * min(1.0, t / total)))
    if bar_w > 0:
        arr[:bar_h, :bar_w] = color
    return arr


def typewriter_slice(main_lines: list, sub_lines: list,
                     elapsed: float, speed: float):
    all_lines = main_lines + sub_lines
    total = sum(len(l) for l in all_lines)
    shown = min(total, int(elapsed * speed))
    r_main, r_sub, rem = [], [], shown
    for line in main_lines:
        if rem <= 0:
            break
        take = min(len(line), rem)
        r_main.append(line[:take])
        rem -= take
    for line in sub_lines:
        if rem <= 0:
            break
        take = min(len(line), rem)
        r_sub.append(line[:take])
        rem -= take
    return r_main or [""], r_sub


def get_box_y(position: str, h: int, box_h: int) -> int:
    if position == "top":
        return int(h * 0.08)
    if position == "center":
        return (h - box_h) // 2
    # bottom: safe zone above Instagram Reels UI (~top 76% of height)
    return int(h * 0.76) - box_h


def render_overlay(
    w: int, h: int,
    main_lines: list, sub_lines: list,
    font_main: ImageFont.FreeTypeFont,
    font_sub: ImageFont.FreeTypeFont,
    position: str, alpha: float, y_shift: int,
    box_color: tuple,
) -> Image.Image:
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    max_lw = 20 if position in ("center", "top") else 28
    wm = sum([textwrap.wrap(l, max_lw) or [""] for l in main_lines], [])
    ws = sum([textwrap.wrap(l, max_lw + 8) or [""] for l in sub_lines], [])

    lhm = font_main.size + 12
    lhs = font_sub.size + 8
    gap = 10
    tot = lhm * len(wm) + (gap + lhs * len(ws) if ws else 0)
    px, py = 30, 18

    mwm = max((draw.textlength(l, font=font_main) for l in wm), default=0)
    mws = max((draw.textlength(l, font=font_sub)  for l in ws),  default=0)
    bw  = max(mwm, mws) + 2 * px
    bx  = (w - bw) / 2
    by  = get_box_y(position, h, tot + 2 * py) + y_shift
    bx2 = bx + bw
    by2 = by + tot + 2 * py

    draw.rounded_rectangle(
        [bx, by, bx2, by2], radius=14,
        fill=(*box_color[:3], int(box_color[3] * alpha)),
    )

    def put(text, x, y, font):
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, int(210 * alpha)))
        draw.text((x,     y),     text, font=font, fill=(255, 255, 255, int(255 * alpha)))

    y = by + py
    for line in wm:
        put(line, (w - draw.textlength(line, font=font_main)) / 2, y, font_main)
        y += lhm
    if ws:
        y += gap
        for line in ws:
            put(line, (w - draw.textlength(line, font=font_sub)) / 2, y, font_sub)
            y += lhs

    return overlay


def render_auto_caption(
    w: int, h: int,
    caption: dict, t: float,
    font: ImageFont.FreeTypeFont,
    brand_color: tuple,
    y_fraction: float = 0.62,
) -> Image.Image:
    """Render one caption chunk with per-word brand-color highlight."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    words = caption.get("words", [])
    if not words:
        # Fallback: plain text, no word-level data
        text = caption["text"].upper()
        tw = draw.textlength(text, font=font)
        x  = (w - tw) / 2
        y  = int(h * y_fraction)
        px, py = 20, 10
        draw.rounded_rectangle(
            [x - px, y - py, x + tw + px, y + font.size + py],
            radius=8, fill=(0, 0, 0, 140),
        )
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200))
        draw.text((x,     y),     text, font=font, fill=(255, 255, 255, 255))
        return overlay

    # Measure total width for centering
    parts    = [w_["word"].upper() for w_ in words]
    gap_w    = draw.textlength(" ", font=font)
    total_w  = sum(draw.textlength(p, font=font) for p in parts) + gap_w * (len(parts) - 1)
    x_start  = (w - total_w) / 2
    y        = int(h * y_fraction)

    px, py = 20, 10
    draw.rounded_rectangle(
        [x_start - px, y - py, x_start + total_w + px, y + font.size + py],
        radius=8, fill=(0, 0, 0, 140),
    )

    cx = x_start
    for i, (wd, part) in enumerate(zip(words, parts)):
        pw       = draw.textlength(part, font=font)
        is_now   = wd["start"] <= t < wd["end"]
        color    = (*brand_color, 255) if is_now else (255, 255, 255, 255)
        draw.text((cx + 2, y + 2), part, font=font, fill=(0, 0, 0, 200))
        draw.text((cx,     y),     part, font=font, fill=color)
        cx += pw + (gap_w if i < len(parts) - 1 else 0)

    return overlay


def composite_scaled(base: Image.Image, ov: Image.Image, scale: float) -> Image.Image:
    if scale >= 1.0:
        return Image.alpha_composite(base, ov)
    bbox = ov.getbbox()
    if not bbox:
        return base
    region = ov.crop(bbox)
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
    briefing: dict, boundaries: list,
    font_hook, font_cap, font_sub, font_disc,
    vignette: np.ndarray, total_duration: float,
) -> np.ndarray:

    # Ken Burns
    kb = briefing.get("ken_burns", 0.0)
    if kb > 0:
        for i, (cs, ce) in enumerate(boundaries):
            if cs <= t < ce:
                p = (t - cs) / max(0.001, ce - cs)
                scale = (1.0 + kb * p) if i % 2 == 0 else (1.0 + kb * (1 - p))
                frame = apply_ken_burns(frame, scale)
                break

    # Color grade + vignette
    arr = grade_frame(frame, vignette, briefing.get("contrast", 1.12))

    # Text segments
    brand_rgb  = tuple(briefing.get("brand_color", [255, 70, 0]))
    anim_dur   = briefing.get("anim_duration", 0.45)
    type_speed = briefing.get("typewriter_speed", 22)
    fade_out   = 0.3  # seconds before segment end to start fading out

    for seg in briefing.get("segments", []):
        start, end = seg["start"], seg["end"]
        if not (start <= t < end):
            continue

        elapsed   = t - start
        remaining = end - t
        position  = seg.get("position", "bottom")
        anim      = seg.get("anim", "fade")
        main_l    = seg.get("main", [])
        sub_l     = seg.get("sub", [])
        accent    = seg.get("accent", False)

        font_m    = font_hook if position in ("center", "top") else font_cap
        box_color = (*brand_rgb, 200) if accent else (0, 0, 0, 155)

        if anim == "typewriter":
            in_alpha, y_shift, scale = 1.0, 0, 1.0
            ml, sl = typewriter_slice(main_l, sub_l, elapsed, type_speed)

        elif anim == "slide_up":
            p        = min(1.0, elapsed / anim_dur)
            ease     = 1 - (1 - p) ** 3
            in_alpha = p
            y_shift  = int(70 * (1 - ease))
            scale    = 1.0
            ml, sl   = main_l, sub_l

        elif anim == "scale_fade":
            p        = min(1.0, elapsed / anim_dur)
            ease     = 1 - (1 - p) ** 2
            in_alpha = ease
            scale    = 0.78 + 0.22 * ease
            y_shift  = 0
            ml, sl   = main_l, sub_l

        else:  # fade
            in_alpha = min(1.0, elapsed / anim_dur)
            y_shift, scale = 0, 1.0
            ml, sl = main_l, sub_l

        out_alpha = min(1.0, remaining / fade_out)
        alpha     = in_alpha * out_alpha

        h, w  = arr.shape[:2]
        base  = Image.fromarray(arr).convert("RGBA")
        ov    = render_overlay(w, h, ml, sl, font_m, font_sub,
                               position, alpha, y_shift, box_color)

        if anim == "scale_fade" and scale < 1.0:
            result = composite_scaled(base, ov, scale)
        else:
            result = Image.alpha_composite(base, ov)

        arr = np.array(result.convert("RGB"))
        break

    # Auto-captions (Whisper)
    captions      = briefing.get("_captions", [])
    captions_mode = briefing.get("captions_mode", "fill_gaps")
    captions_y    = briefing.get("captions_y", 0.62)
    if captions:
        manual_active = any(
            seg["start"] <= t < seg["end"]
            for seg in briefing.get("segments", [])
        )
        show_caption = (captions_mode == "always") or not manual_active
        if show_caption:
            for cap in captions:
                if cap["start"] <= t < cap["end"]:
                    h, w  = arr.shape[:2]
                    base  = Image.fromarray(arr).convert("RGBA")
                    cap_ov = render_auto_caption(
                        w, h, cap, t, font_cap,
                        brand_rgb, captions_y,
                    )
                    arr = np.array(Image.alpha_composite(base, cap_ov).convert("RGB"))
                    break

    # Disclaimer
    disc_text  = briefing.get("disclaimer", "")
    disc_start = briefing.get("disclaimer_start", 9999)
    if disc_text and t >= disc_start:
        h, w  = arr.shape[:2]
        base  = Image.fromarray(arr).convert("RGBA")
        dov   = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd    = ImageDraw.Draw(dov)
        dw    = dd.textlength(disc_text, font=font_disc)
        dx    = (w - dw) / 2
        dy    = h - 50
        dd.text((dx + 1, dy + 1), disc_text, font=font_disc, fill=(0, 0, 0, 180))
        dd.text((dx,     dy),     disc_text, font=font_disc, fill=(255, 255, 255, 200))
        arr   = np.array(Image.alpha_composite(base, dov).convert("RGB"))

    # Progress bar
    if briefing.get("progress_bar", True):
        bar_h = briefing.get("progress_bar_height", 5)
        arr   = draw_progress_bar(arr, t, total_duration, brand_rgb, bar_h)

    return arr


def run(briefing_path: str, output_path: str, extra_inputs: list = None):
    briefing    = json.loads(Path(briefing_path).read_text(encoding="utf-8"))
    input_paths = extra_inputs if extra_inputs else briefing.get("inputs", [])

    # Load auto-captions if specified
    caps_file = briefing.get("captions_file", "")
    if caps_file and Path(caps_file).exists():
        briefing["_captions"] = json.loads(Path(caps_file).read_text(encoding="utf-8"))
        print(f"Loaded {len(briefing['_captions'])} caption chunks from {caps_file}")

    clips = [VideoFileClip(p) for p in input_paths]
    clip  = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]
    total_duration = clip.duration

    boundaries, t0 = [], 0.0
    for c in clips:
        boundaries.append((t0, t0 + c.duration))
        t0 += c.duration

    h_px, w_px = clip.size[1], clip.size[0]
    vignette   = build_vignette(h_px, w_px, briefing.get("vignette", 0.55))

    font_hook = load_font(briefing.get("font_size_hook",       66), role="title")
    font_cap  = load_font(briefing.get("font_size_caption",    48), role="body")
    font_sub  = load_font(briefing.get("font_size_sub",        32), role="body")
    font_disc = load_font(briefing.get("font_size_disclaimer", 22), role="body")

    def add_effects(get_frame, t):
        return process_frame(
            get_frame(t), t, briefing, boundaries,
            font_hook, font_cap, font_sub, font_disc,
            vignette, total_duration,
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
        print("Usage: python3 add_text_overlay.py briefing.json output.mp4 [input.mp4 ...]")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3:] or None)
