"""
make_slideshow.py — Instagram Reels from still photos.
Ken Burns, cross-dissolve transitions, text overlay, grade, CTA frame.

Usage:
    python3 make_slideshow.py briefing.json output.mp4
"""

import sys
import json
import textwrap
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip


# ── Font loader ───────────────────────────────────────────────────────────────
_font_cache: dict = {}
_FONTS_DIR = Path(__file__).parent / "fonts"

_TITLE_FONTS = [
    str(_FONTS_DIR / "HKModular-Bold.ttf"),
    str(_FONTS_DIR / "HKModular-Black.ttf"),
    str(_FONTS_DIR / "BarlowCondensed-Black.ttf"),
    str(_FONTS_DIR / "BarlowCondensed-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_BODY_FONTS = [
    str(_FONTS_DIR / "Montserrat-Bold.ttf"),
    str(_FONTS_DIR / "Montserrat-SemiBold.ttf"),
    str(_FONTS_DIR / "BarlowCondensed-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def load_font(size: int, role: str = "body") -> ImageFont.FreeTypeFont:
    key = (size, role)
    if key not in _font_cache:
        candidates = _TITLE_FONTS if role == "title" else _BODY_FONTS
        f = ImageFont.load_default()
        for p in candidates:
            try:
                f = ImageFont.truetype(p, size)
                break
            except OSError:
                pass
        _font_cache[key] = f
    return _font_cache[key]


# ── Image utils ───────────────────────────────────────────────────────────────
def load_portrait(path: str, out_w: int = 1080, out_h: int = 1920) -> np.ndarray:
    """Load image and crop to portrait (9:16) using cover strategy."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if (w / h) > (out_w / out_h):
        scale = out_h / h
        img = img.resize((int(w * scale), out_h), Image.LANCZOS)
        x0 = (img.width - out_w) // 2
        img = img.crop((x0, 0, x0 + out_w, out_h))
    else:
        scale = out_w / w
        img = img.resize((out_w, int(h * scale)), Image.LANCZOS)
        y0 = (img.height - out_h) // 2
        img = img.crop((0, y0, out_w, y0 + out_h))
    return np.array(img)


def ken_burns(img: np.ndarray, t: float, duration: float,
              zoom: float = 0.12, direction: str = "in_center") -> np.ndarray:
    """Directional Ken Burns. Directions: in_center out_center right left up down in_tl in_br diagonal."""
    h, w = img.shape[:2]
    p = t / max(duration, 0.001)
    p_e = 1 - (1 - p) ** 2  # ease-out progress

    if direction == "in_center":
        scale = 1.0 + zoom * p_e
        xf, yf = 0.5, 0.5
    elif direction == "out_center":
        scale = 1.0 + zoom * (1 - p_e)
        xf, yf = 0.5, 0.5
    elif direction == "right":
        scale = 1.0 + zoom * 0.4
        xf, yf = 0.25 + 0.5 * p_e, 0.5
    elif direction == "left":
        scale = 1.0 + zoom * 0.4
        xf, yf = 0.75 - 0.5 * p_e, 0.5
    elif direction == "up":
        scale = 1.0 + zoom * 0.4
        xf, yf = 0.5, 0.7 - 0.4 * p_e
    elif direction == "down":
        scale = 1.0 + zoom * 0.4
        xf, yf = 0.5, 0.3 + 0.4 * p_e
    elif direction == "in_tl":
        scale = 1.0 + zoom * p_e
        xf, yf = 0.3, 0.25
    elif direction == "in_br":
        scale = 1.0 + zoom * p_e
        xf, yf = 0.7, 0.75
    elif direction == "diagonal":
        scale = 1.0 + zoom * p_e
        xf = 0.25 + 0.5 * p_e
        yf = 0.75 - 0.5 * p_e
    else:
        scale = 1.0 + zoom * p_e
        xf, yf = 0.5, 0.5

    nh, nw = max(1, int(h / scale)), max(1, int(w / scale))
    y0 = max(0, min(int((h - nh) * yf), h - nh))
    x0 = max(0, min(int((w - nw) * xf), w - nw))
    cropped = img[y0:y0 + nh, x0:x0 + nw]
    return np.array(Image.fromarray(cropped).resize((w, h), Image.BILINEAR))


def build_vignette(h: int, w: int, strength: float = 0.6) -> np.ndarray:
    Y = np.linspace(-1, 1, h)[:, None]
    X = np.linspace(-1, 1, w)[None, :]
    mask = 1.0 - np.clip(np.sqrt(X**2 + Y**2) / np.sqrt(2) * strength, 0, 1)
    return mask[:, :, None]


def grade(arr: np.ndarray, vignette: np.ndarray, contrast: float = 1.15) -> np.ndarray:
    f = (arr.astype(np.float32) - 128) * contrast + 128
    return np.clip(f * vignette, 0, 255).astype(np.uint8)


def make_cta_bg(w: int, h: int, brand_color: list) -> np.ndarray:
    """Deep navy-blue vertical gradient for CTA slides — white text on blue."""
    top    = np.array([8, 30, 100], dtype=np.float32)
    bottom = np.array([3, 14,  58], dtype=np.float32)
    t_grad = np.linspace(0, 1, h)[:, None, None]
    arr    = top * (1 - t_grad) + bottom * t_grad
    return np.tile(arr, (1, w, 1)).astype(np.uint8)


# ── Text rendering ────────────────────────────────────────────────────────────
def box_y(position: str, h: int, box_h: int) -> int:
    if position == "top":    return int(h * 0.07)
    if position == "center": return (h - box_h) // 2
    return int(h * 0.76) - box_h


def render_text_ov(
    w: int, h: int,
    main_lines: list, sub_lines: list,
    font_main, font_sub,
    position: str, alpha: float,
    brand_color: tuple, y_shift: int = 0, scale: float = 1.0,
    accent: bool = False,
) -> Image.Image:
    wm = sum([textwrap.wrap(l, 22) or [""] for l in main_lines], [])
    ws = sum([textwrap.wrap(l, 28) or [""] for l in sub_lines], [])

    lhm = font_main.size + 8
    lhs = font_sub.size + 6
    gap = 10
    py  = 14
    tot = lhm * len(wm) + (gap + lhs * len(ws) if ws else 0)

    ov   = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)
    by   = box_y(position, h, tot + 2 * py) + y_shift

    # Full-width scrim for bottom/top — cinematic, no rounded box
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

    # Thin brand-color accent line
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

    # Scale-in for scale_fade anim (center only — no scrim to distort)
    if scale < 1.0 and position == "center":
        bbox = ov.getbbox()
        if bbox:
            region = ov.crop(bbox)
            nw2 = max(1, int((bbox[2] - bbox[0]) * scale))
            nh2 = max(1, int((bbox[3] - bbox[1]) * scale))
            region = region.resize((nw2, nh2), Image.LANCZOS)
            cx = (bbox[0] + bbox[2]) // 2
            cy = (bbox[1] + bbox[3]) // 2
            ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ov.paste(region, (cx - nw2 // 2, cy - nh2 // 2), region)

    return ov


def ease_out_back(p: float, overshoot: float = 0.25) -> float:
    """Ease-out with slight overshoot — text 'pops' past 1.0 then settles."""
    c1 = overshoot
    c3 = c1 + 1
    return 1 + c3 * ((p - 1) ** 3) + c1 * ((p - 1) ** 2)


def progress_bar(arr: np.ndarray, t: float, total: float,
                 color: tuple, bar_h: int = 5) -> np.ndarray:
    bar_w = max(0, int(arr.shape[1] * min(1.0, t / total)))
    if bar_w > 0:
        out = arr.copy()
        out[:bar_h, :bar_w] = color
        return out
    return arr


# ── Slide renderer ────────────────────────────────────────────────────────────
def render_slide(slide: dict, local_t: float, imgs: dict,
                 vignette: np.ndarray, fonts: dict,
                 brand_color: list, anim_dur: float = 0.30) -> np.ndarray:
    dur      = slide["duration"]
    is_cta   = slide.get("type") == "cta"
    h, w     = vignette.shape[:2]
    fade_out = 0.30

    # Base image
    if is_cta:
        arr = make_cta_bg(w, h, brand_color)
    else:
        arr = ken_burns(
            imgs[slide["image"]], local_t, dur,
            zoom=slide.get("kb_zoom", 0.12),
            direction=slide.get("kb_direction", "in_center"),
        )
        arr = grade(arr, vignette, contrast=1.18)

    # Text params
    position  = slide.get("position", "bottom")
    anim      = slide.get("anim", "fade")
    main_l    = slide.get("main", [])
    sub_l     = slide.get("sub", [])
    accent    = slide.get("accent", False)
    brand_rgb = tuple(brand_color[:3])

    elapsed   = local_t
    remaining = dur - local_t

    if anim == "typewriter":
        total_chars = sum(len(l) for l in main_l + sub_l)
        shown = min(total_chars, int(elapsed * 28))  # faster type speed
        ml, sl, rem = [], [], shown
        for line in main_l:
            take = min(len(line), rem); ml.append(line[:take]); rem -= take
        for line in sub_l:
            if rem <= 0: break
            take = min(len(line), rem); sl.append(line[:take]); rem -= take
        ml = ml or [""]
        in_alpha, y_shift, sc = 1.0, 0, 1.0
        main_r, sub_r = ml, sl

    elif anim == "scale_fade":
        p = min(1.0, elapsed / anim_dur)
        # ease-out-back: text POPs past 1.0 and settles
        ease_scale = min(ease_out_back(p, overshoot=0.22), 1.15)
        ease_alpha = 1 - (1 - p) ** 2
        in_alpha = ease_alpha
        sc       = 0.70 + 0.30 * ease_scale  # starts at 0.70, overshoots ~1.07
        y_shift  = 0
        main_r, sub_r = main_l, sub_l

    elif anim == "slide_up":
        p = min(1.0, elapsed / anim_dur)
        ease = 1 - (1 - p) ** 3
        in_alpha = p
        y_shift  = int(70 * (1 - ease))
        sc       = 1.0
        main_r, sub_r = main_l, sub_l

    else:  # fade
        in_alpha, y_shift, sc = min(1.0, elapsed / anim_dur), 0, 1.0
        main_r, sub_r = main_l, sub_l

    alpha = in_alpha * min(1.0, remaining / fade_out)

    base = Image.fromarray(arr).convert("RGBA")
    ov   = render_text_ov(w, h, main_r, sub_r, fonts["main"], fonts["sub"],
                           position, alpha, brand_rgb, y_shift, sc, accent)
    return np.array(Image.alpha_composite(base, ov).convert("RGB"))


# ── Main ──────────────────────────────────────────────────────────────────────
def run(briefing_path: str, output_path: str):
    cfg         = json.loads(Path(briefing_path).read_text(encoding="utf-8"))
    brand_color = cfg.get("brand_color", [255, 70, 0])
    out_w, out_h = cfg.get("output_size", [1080, 1920])
    fps         = cfg.get("fps", 30)
    trans_dur   = cfg.get("transition_dur", 0.6)
    slides_data = cfg["slides"]

    # Pre-load images
    imgs = {}
    for slide in slides_data:
        path = slide.get("image", "")
        if path and path not in imgs:
            print(f"Loading {Path(path).name}...")
            imgs[path] = load_portrait(path, out_w, out_h)

    vignette = build_vignette(out_h, out_w, strength=cfg.get("vignette", 0.62))
    fonts = {
        # font_main > font_hook for backward-compat with existing briefings
        "main": load_font(cfg.get("font_main", cfg.get("font_hook", 52)), role="title"),
        "sub":  load_font(cfg.get("font_sub",  32), role="body"),
    }

    total_duration = sum(s["duration"] for s in slides_data)
    brand_rgb      = tuple(brand_color[:3])

    def make_frame(t):
        cumulative = 0.0
        for i, slide in enumerate(slides_data):
            slide_end = cumulative + slide["duration"]
            if t < slide_end or i == len(slides_data) - 1:
                local_t    = t - cumulative
                remaining  = slide_end - t
                transition = slide.get("transition", "dissolve")

                current = render_slide(slide, local_t, imgs, vignette, fonts, brand_color)

                if i + 1 < len(slides_data):
                    if transition == "cut":
                        # Brief white flash: last 2 frames out, first 2 frames in
                        flash_out = remaining * fps
                        flash_in  = local_t * fps
                        if flash_out < 2:
                            strength = (1 - flash_out / 2) * 0.65
                            current  = np.clip(
                                current.astype(np.float32) * (1 - strength) + 255 * strength, 0, 255
                            ).astype(np.uint8)
                        elif flash_in < 2:
                            strength = (1 - flash_in / 2) * 0.65
                            current  = np.clip(
                                current.astype(np.float32) * (1 - strength) + 255 * strength, 0, 255
                            ).astype(np.uint8)
                    else:  # dissolve
                        if remaining < trans_dur:
                            alpha_next = 1.0 - (remaining / trans_dur)
                            nxt = render_slide(slides_data[i + 1], 0.0, imgs, vignette, fonts, brand_color)
                            current = ((1 - alpha_next) * current + alpha_next * nxt).astype(np.uint8)

                # Progress bar
                current = progress_bar(current, t, total_duration, brand_rgb)
                return current
            cumulative += slide["duration"]

        last = render_slide(slides_data[-1], slides_data[-1]["duration"] - 0.001,
                            imgs, vignette, fonts, brand_color)
        return progress_bar(last, t, total_duration, brand_rgb)

    print(f"Rendering {total_duration:.1f}s at {fps}fps → {output_path}")
    VideoClip(make_frame, duration=total_duration).write_videofile(
        output_path, fps=fps, codec="libx264", audio=False, logger="bar",
    )
    print(f"\nDone! → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 make_slideshow.py briefing.json output.mp4")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
