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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, concatenate_videoclips


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


def cinematic_grade(arr: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Teal-orange cinematic grade: cool shadows, warm highlights."""
    f   = arr.astype(np.float32) / 255.0
    lum = (0.299 * f[:,:,0] + 0.587 * f[:,:,1] + 0.114 * f[:,:,2])[:,:,None]
    sha = np.clip(1.0 - lum / 0.4, 0, 1)   # shadow mask
    hil = np.clip((lum - 0.6) / 0.4, 0, 1) # highlight mask
    s   = strength * 0.07
    out = np.stack([
        np.clip(f[:,:,0] - sha[:,:,0]*s + hil[:,:,0]*s*1.1, 0, 1),
        np.clip(f[:,:,1] + sha[:,:,0]*s*0.3, 0, 1),
        np.clip(f[:,:,2] + sha[:,:,0]*s*1.1 - hil[:,:,0]*s, 0, 1),
    ], axis=2)
    return (out * 255).astype(np.uint8)


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
    brand_color: tuple, accent: bool = False,
) -> Image.Image:
    max_m = 22 if position == "center" else 28
    wm = sum([textwrap.wrap(l, max_m) or [""] for l in main_lines], [])
    ws = sum([textwrap.wrap(l, 32) or [""] for l in sub_lines], [])

    lhm = font_main.size + 8
    lhs = font_sub.size + 6
    gap = 10
    py  = 14
    tot = lhm * len(wm) + (gap + lhs * len(ws) if ws else 0)
    by  = get_box_y(position, h, tot + 2 * py) + y_shift

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    # Subtle full-width scrim at bottom/top — cinematic, no rounded box
    if position != "center":
        draw.rectangle(
            [0, by - py, w, by + tot + py],
            fill=(0, 0, 0, int(72 * alpha)),
        )

    # Main text — crisp white, no offset shadow
    yt, widths = by, []
    for line in wm:
        lw = draw.textlength(line, font=font_main)
        widths.append(lw)
        draw.text(((w - lw) / 2, yt), line, font=font_main,
                  fill=(255, 255, 255, int(255 * alpha)))
        yt += lhm

    # Thin brand-color accent line below main text
    if accent and widths:
        max_w = max(widths)
        draw.rectangle(
            [(w - max_w) / 2, yt + 5, (w + max_w) / 2, yt + 8],
            fill=(*brand_color[:3], int(255 * alpha)),
        )

    # Sub text — slightly off-white
    if ws:
        yt += gap
        for line in ws:
            lw = draw.textlength(line, font=font_sub)
            draw.text(((w - lw) / 2, yt), line, font=font_sub,
                      fill=(205, 215, 230, int(215 * alpha)))
            yt += lhs

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
    font_main, font_sub, font_disc,
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

    # Color grade + vignette + optional cinematic look
    arr = grade_frame(frame, vignette, briefing.get("contrast", 1.12))
    if briefing.get("color_grade") == "cinematic":
        arr = cinematic_grade(arr, briefing.get("cinematic_strength", 1.0))

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

        elif anim == "word_reveal":
            words_all   = " ".join(main_l).split()
            timings     = seg.get("word_timing", [i * 0.5 for i in range(len(words_all))])
            shown_count = sum(1 for ts in timings if elapsed >= ts)
            shown       = words_all[:shown_count]
            ml          = [" ".join(shown)] if shown else [""]
            sl          = sub_l
            first_ts    = timings[0] if timings else 0.0
            in_alpha    = min(1.0, max(0.0, elapsed - first_ts) / 0.20) if shown_count > 0 else 0.0
            y_shift, scale = 0, 1.0

        else:  # fade
            in_alpha = min(1.0, elapsed / anim_dur)
            y_shift, scale = 0, 1.0
            ml, sl = main_l, sub_l

        out_alpha = min(1.0, remaining / fade_out)
        alpha     = in_alpha * out_alpha

        h, w  = arr.shape[:2]
        base  = Image.fromarray(arr).convert("RGBA")
        ov    = render_overlay(w, h, ml, sl, font_main, font_sub,
                               position, alpha, y_shift, brand_rgb, accent)

        if anim == "scale_fade" and scale < 1.0 and position == "center":
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
                        w, h, cap, t, font_sub,
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

    # Logo overlay
    logo_img = briefing.get("_logo_img")
    if logo_img is not None:
        segs          = briefing.get("segments", [])
        logo_start    = briefing.get("logo_start", segs[-1]["start"] if segs else 0)
        logo_end      = briefing.get("logo_end",   segs[-1]["end"]   if segs else total_duration)
        if logo_start <= t < logo_end:
            elapsed_logo   = t - logo_start
            remaining_logo = logo_end - t
            fade_dur = briefing.get("logo_fade_dur", 0.55)
            in_a     = min(1.0, elapsed_logo   / fade_dur)
            out_a    = min(1.0, remaining_logo / 0.30)
            logo_alpha = (1 - (1 - in_a) ** 2) * out_a   # ease-out in, hard out

            h, w = arr.shape[:2]
            lw, lh = logo_img.size
            lx = (w - lw) // 2
            y_frac = briefing.get("logo_y_frac", 0.38)
            ly = int(h * y_frac) - lh // 2

            # Apply alpha by scaling logo's A channel
            r, g, b, a = logo_img.split()
            a = a.point(lambda x: int(x * logo_alpha))
            logo_frame = Image.merge("RGBA", (r, g, b, a))

            base_img = Image.fromarray(arr).convert("RGBA")
            base_img.paste(logo_frame, (lx, ly), logo_frame)
            arr = np.array(base_img.convert("RGB"))

    # Progress bar
    if briefing.get("progress_bar", True):
        bar_h = briefing.get("progress_bar_height", 5)
        arr   = draw_progress_bar(arr, t, total_duration, brand_rgb, bar_h)

    # Letterbox — thin black bars for cinematic feel
    lb = briefing.get("letterbox", 0)
    if lb > 0:
        arr = arr.copy()
        arr[:lb]    = 0
        arr[-lb:]   = 0

    return arr


def run(briefing_path: str, output_path: str, extra_inputs: list = None):
    briefing    = json.loads(Path(briefing_path).read_text(encoding="utf-8"))
    input_paths = extra_inputs if extra_inputs else briefing.get("inputs", [])

    # Load auto-captions if specified
    caps_file = briefing.get("captions_file", "")
    if caps_file and Path(caps_file).exists():
        briefing["_captions"] = json.loads(Path(caps_file).read_text(encoding="utf-8"))
        print(f"Loaded {len(briefing['_captions'])} caption chunks from {caps_file}")

    clip_trim  = briefing.get("clip_trim", [])
    audio_fade = briefing.get("audio_fade", 0.0)
    audio_vol  = briefing.get("audio_volume", 1.0)

    clips = []
    for i, p in enumerate(input_paths):
        c = VideoFileClip(p)
        if i < len(clip_trim) and clip_trim[i] and c.duration > clip_trim[i]:
            c = c.subclipped(0, clip_trim[i])
        clips.append(c)

    # Audio smoothing at clip boundaries
    if clips and (audio_fade > 0 or audio_vol != 1.0):
        try:
            from moviepy.audio.fx import AudioFadeOut, AudioFadeIn
            smoothed = []
            for i, c in enumerate(clips):
                if c.audio is None:
                    smoothed.append(c)
                    continue
                if audio_vol != 1.0:
                    c = c.with_volume_scaled(audio_vol)
                if audio_fade > 0:
                    fade = min(audio_fade, c.duration * 0.4)
                    effects = []
                    if i < len(clips) - 1:
                        effects.append(AudioFadeOut(fade))
                    if i > 0:
                        effects.append(AudioFadeIn(fade))
                    if effects:
                        c = c.with_effects(effects)
                smoothed.append(c)
            clips = smoothed
        except Exception as e:
            print(f"Audio fx skipped: {e}")

    clip = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]
    total_duration = clip.duration

    # Optional background music overlay
    music_path = briefing.get("music")
    if music_path and Path(music_path).exists():
        try:
            from moviepy import AudioFileClip, concatenate_audioclips
            from moviepy.audio import CompositeAudioClip
            music = AudioFileClip(music_path)
            if music.duration < total_duration:
                loops = int(np.ceil(total_duration / music.duration))
                music = concatenate_audioclips([music] * loops)
            music = music.subclipped(0, total_duration).with_volume_scaled(
                briefing.get("music_volume", 0.5)
            )
            orig = clip.audio
            if orig:
                from moviepy.audio import CompositeAudioClip
                clip = clip.with_audio(CompositeAudioClip([orig, music]))
            else:
                clip = clip.with_audio(music)
            print(f"Music overlay: {Path(music_path).name}")
        except Exception as e:
            print(f"Music overlay skipped: {e}")

    max_dur = briefing.get("duration")
    if max_dur and clip.duration > max_dur:
        clip = clip.subclipped(0, max_dur)
        total_duration = max_dur

    boundaries, t0 = [], 0.0
    for c in clips:
        boundaries.append((t0, t0 + c.duration))
        t0 += c.duration

    h_px, w_px = clip.size[1], clip.size[0]
    vignette   = build_vignette(h_px, w_px, briefing.get("vignette", 0.55))

    # Preload logo PNG (RGBA) into briefing so process_frame can access it
    logo_path = briefing.get("logo", "")
    if logo_path and Path(logo_path).exists():
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_w_pct = briefing.get("logo_width_pct", 0.55)
        target_w   = int(w_px * logo_w_pct)
        ratio      = target_w / logo_img.width
        target_h   = max(1, int(logo_img.height * ratio))
        briefing["_logo_img"] = logo_img.resize((target_w, target_h), Image.LANCZOS)
        print(f"Logo: {Path(logo_path).name}  →  {target_w}×{target_h}px")
    else:
        briefing.pop("_logo_img", None)

    # Backward-compatible: font_size_main > font_size_hook fallback
    font_main = load_font(
        briefing.get("font_size_main", briefing.get("font_size_hook", 44)),
        role="title",
    )
    font_sub  = load_font(briefing.get("font_size_sub",        28), role="body")
    font_disc = load_font(briefing.get("font_size_disclaimer", 20), role="body")

    def add_effects(get_frame, t):
        return process_frame(
            get_frame(t), t, briefing, boundaries,
            font_main, font_sub, font_disc,
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
