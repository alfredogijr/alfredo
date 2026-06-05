#!/usr/bin/env python3
"""
MetaKart Weekly Ranking Image Generator

Usage:
  python generate_ranking.py \
    --barra barra.pdf \
    --norte norte.pdf \
    --campo-grande campo_grande.pdf \
    [--period "25/05/2026 a 31/05/2026"]

Outputs to output/instagram/ (1080×1350) and output/tv/ (1920×1080).
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime

import pdfplumber
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# OCR support (lazy imports — only used for scanned PDFs)
try:
    import fitz as _fitz          # PyMuPDF
    import pytesseract as _tess
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False

# ─── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
FONTS    = BASE_DIR / "assets" / "fonts"
LOGO     = BASE_DIR / "assets" / "logo_metakart.png"
LOGO_W   = BASE_DIR / "assets" / "logo_metakart_white.png"
OUT_IG   = BASE_DIR / "output" / "instagram"
OUT_TV   = BASE_DIR / "output" / "tv"

# ─── Track Config ──────────────────────────────────────────────────────────────

TRACKS = {
    "barra": {
        "name":          "BARRA",
        "primary":       (108,  52, 200),
        "primary_dark":  ( 48,  18,  95),
        "primary_light": (185, 128, 255),
        "bg":            ( 60,  25, 130),   # medium-dark purple — matches cover
        "row_bg":        ( 82,  38, 165),
        "num_bg":        ( 40,  12,  90),
    },
    "norte": {
        "name":          "NORTE",
        "primary":       ( 22, 150,  48),
        "primary_dark":  (  8,  55,  18),
        "primary_light": ( 60, 215,  88),
        "bg":            ( 14,  85,  30),   # medium-dark green — matches cover
        "row_bg":        ( 20, 110,  40),
        "num_bg":        (  8,  55,  18),
    },
    "campo_grande": {
        "name":          "CAMPO GRANDE",
        "primary":       (253, 131,  48),   # #fd8330 — cor oficial
        "primary_dark":  (160,  65,   0),
        "primary_light": (255, 180,  95),
        "bg":            (210,  85,   8),   # tom escuro do #fd8330
        "row_bg":        (175,  68,   0),
        "num_bg":        (130,  50,   0),
    },
}

# ─── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class Entry:
    pos:  int
    name: str
    time: str


@dataclass
class Category:
    label:   str
    entries: List[Entry] = field(default_factory=list)


@dataclass
class Track:
    key:          str
    period_start: str
    period_end:   str
    categories:   List[Category] = field(default_factory=list)


# ─── PDF Parsing ───────────────────────────────────────────────────────────────

_TIME_RE  = re.compile(r'\b(\d{2}:\d{2}:\d{3})\b')
_DATE_RE  = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
# Anchor: find a date then capture the very next token (the time, possibly garbled)
_DATE_TIME_ANCHOR = re.compile(r'(\d{2}/\d{2}/\d{4})\s+(\S+)')

_CAT_MAP = [
    (re.compile(r'A PARTIR DE 90',    re.I), "ACIMA 90KG"),
    (re.compile(r'AT[EÉ] 75 KG',      re.I), "ATÉ 75KG"),
    (re.compile(r'DE 75 KG AT[EÉ] 90',re.I), "DE 75KG A 90KG"),
]

_SKIP_RE = re.compile(
    r'RANKING MENSAL|LAPTIME|SISECOM|DATA/HORA|'
    r'\bCompetidor\b|\bEmail\b|\bTelefone\b|\bPeso\b|\bData\b|'
    r'Pista \d|Norte Shopping|Shopping Metropolitano|Campo Grande Shopping|'
    r'Página \d|Digitalizado|LapTime|INDOOR KARTING|META KART',
    re.IGNORECASE
)


def _fmt_time_clean(raw: str) -> str:
    """'00:31:717' → '31.717' for well-formed times."""
    parts = raw.split(":")
    return f"{parts[1]}.{parts[2]}" if len(parts) == 3 else raw


def _fmt_time_ocr(tok: str) -> Optional[str]:
    """Parse a possibly-garbled OCR time token like '0031:293' or '00;31:323'."""
    digits = re.sub(r'\D', '', tok)
    if not digits.startswith('0'):
        return None
    if len(digits) == 7:                         # normal: 00SSMMM
        return f"{digits[2:4]}.{digits[4:7]}"
    if len(digits) == 8:                         # OCR artefact: 00XSSMMM (X = misread ':')
        return f"{digits[3:5]}.{digits[5:8]}"
    if len(digits) == 6:                         # truncated ms: 00SSMM → pad
        return f"{digits[2:4]}.{digits[4:6]}0"
    return None


def _extract_name(line: str, stop: int) -> str:
    """Extract competitor name, stopping at email/phone/date tokens."""
    tokens = line[:stop].split()
    parts = []
    for tok in tokens:
        if _DATE_RE.match(tok):
            break
        if '@' in tok:
            break
        # Phone number
        clean = re.sub(r'[\s\-\(\)\+\.]', '', tok)
        if len(clean) >= 7 and clean.isdigit():
            break
        # Email fragment: long all-lowercase token (email username without @)
        if re.match(r'^[a-z][a-z0-9._]{9,}$', tok):
            break
        parts.append(tok)
    name = ' '.join(parts).strip()
    return name.upper() if len(name) >= 3 else ""


def _is_scanned(path: str) -> bool:
    """Return True if the PDF has no embedded text (needs OCR)."""
    with pdfplumber.open(path) as pdf:
        total = sum(len(p.extract_text() or "") for p in pdf.pages)
    return total < 50


def _ocr_lines(path: str) -> List[str]:
    """Render PDF pages as images and run Tesseract OCR."""
    if not _OCR_AVAILABLE:
        raise RuntimeError(
            "PyMuPDF/pytesseract not available. Install with:\n"
            "  pip install pymupdf pytesseract\n"
            "  apt-get install tesseract-ocr tesseract-ocr-por"
        )
    doc = _fitz.open(path)
    lines: List[str] = []
    for page in doc:
        mat = _fitz.Matrix(2.5, 2.5)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = _tess.image_to_string(img, lang="por+eng")
        lines.extend(text.split("\n"))
    return lines


def _parse_lines(lines: List[str], ocr: bool) -> tuple:
    """Parse ranking lines, returning (sections dict, race_dates list)."""
    sections: dict = {}
    race_dates: List[datetime] = []
    cur: Optional[str] = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Category header?
        matched_cat = None
        for pat, label in _CAT_MAP:
            if pat.search(line):
                matched_cat = label
                break
        if matched_cat:
            cur = matched_cat
            sections.setdefault(cur, [])
            continue

        if cur is None or _SKIP_RE.search(line):
            continue

        if ocr:
            # Use date as anchor to find the (possibly garbled) time token
            m = _DATE_TIME_ANCHOR.search(line)
            if not m:
                continue
            try:
                race_dates.append(datetime.strptime(m.group(1), "%d/%m/%Y"))
            except ValueError:
                pass
            time_str = _fmt_time_ocr(m.group(2))
            if not time_str:
                continue
            name = _extract_name(line, m.start())
        else:
            # Well-formed digital PDF
            tm = _TIME_RE.search(line)
            if not tm:
                continue
            for dm in _DATE_RE.finditer(line):
                try:
                    race_dates.append(datetime.strptime(dm.group(1), "%d/%m/%Y"))
                except ValueError:
                    pass
            time_str = _fmt_time_clean(tm.group(1))
            name = _extract_name(line, tm.start())

        if name:
            sections[cur].append((name, time_str))

    return sections, race_dates


def parse_pdf(path: str, key: str) -> Track:
    scanned = _is_scanned(path)
    lines   = _ocr_lines(path) if scanned else []

    if not scanned:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines.extend(text.split("\n"))

    sections, race_dates = _parse_lines(lines, ocr=scanned)

    period_start = min(race_dates).strftime("%d/%m/%Y") if race_dates else ""
    period_end   = max(race_dates).strftime("%d/%m/%Y") if race_dates else ""

    order = ["ATÉ 75KG", "DE 75KG A 90KG", "ACIMA 90KG"]
    categories = []
    for label in order:
        data = sections.get(label, [])
        if data:
            categories.append(Category(
                label=label,
                entries=[Entry(i + 1, n, t) for i, (n, t) in enumerate(data[:10])]
            ))

    return Track(
        key=key,
        period_start=period_start,
        period_end=period_end,
        categories=categories,
    )


# ─── Font Cache ────────────────────────────────────────────────────────────────

_font_cache: dict = {}

def font(style: str, size: int) -> ImageFont.FreeTypeFont:
    key = (style, size)
    if key not in _font_cache:
        paths = {
            "title":    FONTS / "BebasNeue-Regular.ttf",
            "bold":     FONTS / "Montserrat-Bold.ttf",
            "semibold": FONTS / "Montserrat-SemiBold.ttf",
            "regular":  FONTS / "Montserrat-Regular.ttf",
        }
        _font_cache[key] = ImageFont.truetype(str(paths[style]), size)
    return _font_cache[key]


# ─── Drawing Helpers ───────────────────────────────────────────────────────────

def _lerp_color(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def _lum(c: tuple) -> float:
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255


def _text_on(bg: tuple) -> tuple:
    """White or near-black — whichever contrasts best with the given background."""
    if _lum(bg) > 0.52:
        return (22, 22, 28)
    return (255, 255, 255)


def _add_halftone(img: Image.Image, step: int = 14, dot_r: int = 3,
                  max_alpha: int = 22) -> Image.Image:
    """Subtle white dot halftone overlay, fading to edges (matches brand style)."""
    W, H  = img.size
    ov    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(ov)
    cx, cy   = W / 2, H / 2
    max_dist = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(0, H + step, step):
        for x in range(0, W + step, step):
            dist  = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            fade  = max(0.0, 1.0 - (dist / max_dist) ** 0.7)
            a     = int(max_alpha * fade)
            if a > 2:
                draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r],
                             fill=(255, 255, 255, a))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def _place_logo_white(img: Image.Image, y_center: int,
                      max_w: int, max_h: int,
                      x_center: int = -1, container_w: int = -1) -> None:
    """Place white logo (transparent bg) for dark backgrounds.

    container_w: if >= 0, center logo within a container of this width starting at x=0.
    x_center: if >= 0, use as left x of the paste operation (overrides container_w).
    Default: center on full image width.
    """
    src  = LOGO_W if LOGO_W.exists() else LOGO
    logo = Image.open(src).convert("RGBA")
    if src == LOGO:
        r, g, b, a = logo.split()
        logo = Image.merge("RGBA", (
            Image.new("L", logo.size, 255),
            Image.new("L", logo.size, 255),
            Image.new("L", logo.size, 255),
            a,
        ))
    # Crop transparent padding so the logo fills the available space correctly
    _, _, _, a = logo.split()
    bbox = a.getbbox()
    if bbox:
        logo = logo.crop(bbox)
    sc   = min(max_w / logo.width, max_h / logo.height)
    lw, lh = int(logo.width * sc), int(logo.height * sc)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    if x_center >= 0:
        cx = x_center
    elif container_w >= 0:
        cx = (container_w - lw) // 2
    else:
        cx = (img.width - lw) // 2
    img.paste(logo, (cx, y_center - lh // 2), logo)


def _row_palette(pos: int, cfg: dict) -> Tuple[tuple, tuple, tuple, tuple]:
    """
    Dark-bg style. Returns (bar_l, bar_r, num_c, text_c).
    pos 1 = primary_light → primary (brightest, hero row).
    pos 2-3 = primary tints.  pos 4+ = row_bg tints.
    All text white on dark.
    """
    white = (255, 255, 255)
    if pos == 1:
        bar_l  = cfg["primary_light"]
        bar_r  = _lerp_color(cfg["primary_light"], cfg["primary"], 0.45)
        num_c  = cfg["primary_dark"]
        text_c = white
    elif pos == 2:
        bar_l  = _lerp_color(cfg["primary_light"], cfg["primary"], 0.45)
        bar_r  = cfg["primary"]
        num_c  = cfg["primary_dark"]
        text_c = white
    elif pos == 3:
        bar_l  = cfg["primary"]
        bar_r  = _lerp_color(cfg["primary"], cfg["row_bg"], 0.40)
        num_c  = cfg["primary_dark"]
        text_c = white
    else:
        bar_l  = cfg["row_bg"]
        bar_r  = _lerp_color(cfg["row_bg"], cfg["bg"], 0.50)
        num_c  = cfg["num_bg"]
        text_c = white
    return bar_l, bar_r, num_c, text_c


def center_text(draw: ImageDraw.Draw, y: int, text: str,
                fnt: ImageFont.FreeTypeFont, color: tuple, canvas_w: int,
                shadow: bool = False) -> int:
    bb  = draw.textbbox((0, 0), text, font=fnt)
    tw  = bb[2] - bb[0]
    x   = (canvas_w - tw) // 2 - bb[0]
    if shadow:
        for ox, oy in [(3, 3), (2, 3), (3, 2)]:
            draw.text((x + ox, y + oy), text, font=fnt, fill=(0, 0, 0, 140))
    draw.text((x, y), text, font=fnt, fill=color)
    return bb[3] - bb[1]


def _gradient_bar(w: int, h: int, col_l: tuple, col_r: tuple) -> Image.Image:
    bar = Image.new("RGB", (w, 1))
    px  = bar.load()
    for x in range(w):
        px[x, 0] = _lerp_color(col_l, col_r, x / max(w - 1, 1))
    return bar.resize((w, h), Image.NEAREST)


def _para_mask(w: int, h: int, slant: int) -> Image.Image:
    """Parallelogram alpha mask — right-leaning (F1 timing-panel style)."""
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([
        (slant, 0), (w - 1, 0),
        (w - 1 - slant, h - 1), (0, h - 1),
    ], fill=255)
    return mask


def _add_radial_glow(img: Image.Image, cx: int, cy: int,
                     radius: int, color: tuple, max_alpha: int = 60) -> Image.Image:
    W, H  = img.size
    glow  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    steps = 22
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(max_alpha * (i / steps) ** 1.8)
        gdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 5))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def _make_checker_faded(size: int, cell: int, color: tuple = (255, 255, 255)) -> Image.Image:
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    n    = size // cell + 2
    diag = (size ** 2 * 2) ** 0.5
    for r in range(n):
        for c in range(n):
            if (r + c) % 2 == 0:
                dist  = ((r * cell) ** 2 + (c * cell) ** 2) ** 0.5
                alpha = int(110 * max(0.0, 1.0 - (dist / diag) * 1.5) ** 1.5)
                if alpha > 4:
                    x1, y1 = c * cell, r * cell
                    draw.rectangle([x1, y1, x1 + cell - 1, y1 + cell - 1],
                                   fill=(*color, alpha))
    return img


def _vertical_gradient(size: tuple, top: tuple, bottom: tuple) -> Image.Image:
    img  = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    w, h = size
    for y in range(h):
        draw.line([(0, y), (w, y)], fill=_lerp_color(top, bottom, y / h))
    return img


def _add_diagonal_band(img: Image.Image, color: tuple,
                       y_left: float = 0.52, y_right: float = 0.30,
                       thickness: float = 0.22, alpha: int = 28) -> Image.Image:
    """Wide diagonal color band — F1 livery element."""
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    yl = int(H * y_left)
    yr = int(H * y_right)
    t  = int(H * thickness)
    ImageDraw.Draw(overlay).polygon([
        (0, yl - t // 2), (W, yr - t // 2),
        (W, yr + t // 2), (0, yl + t // 2),
    ], fill=(*color, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _place_logo(img: Image.Image, y_center: int, max_w: int, max_h: int) -> None:
    logo   = Image.open(LOGO).convert("RGBA")
    sc     = min(max_w / logo.width, max_h / logo.height)
    lw, lh = int(logo.width * sc), int(logo.height * sc)
    logo   = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo, ((img.width - lw) // 2, y_center - lh // 2), logo)


def _draw_row(img: Image.Image, draw: ImageDraw.Draw,
              x: int, y: int, w: int, h: int,
              entry: Entry, cfg: dict, scale: float = 1.0) -> None:
    gap    = int(3 * scale)
    bar_h  = h - gap
    pos_w  = int(h * 0.88)
    slant  = int(bar_h * 0.16)
    stripe = max(4, int(5 * scale))

    bar_l, bar_r, num_c, text_c = _row_palette(entry.pos, cfg)

    # ── Row gradient (parallelogram) ───────────────────────────────────────────
    grad = _gradient_bar(w, bar_h, bar_l, bar_r).convert("RGBA")
    # Subtle shine at top (stronger for pos 1)
    shine_h = max(3, bar_h // (3 if entry.pos == 1 else 6))
    for sy in range(shine_h):
        a = int((52 if entry.pos == 1 else 32) * (1.0 - sy / shine_h) ** 1.4)
        ImageDraw.Draw(grad).line([(0, sy), (w - 1, sy)], fill=(255, 255, 255, a))
    grad.putalpha(_para_mask(w, bar_h, slant))
    img.paste(grad, (x, y), grad)

    # ── Position badge (left parallelogram) ────────────────────────────────────
    badge_w = pos_w + slant
    badge   = Image.new("RGBA", (badge_w, bar_h), (*num_c, 245))
    badge.putalpha(_para_mask(badge_w, bar_h, slant))
    img.paste(badge, (x, y), badge)

    # ── Left accent stripe — primary_light for pos 1, subtle for others ────────
    acc_color = cfg["primary_light"] if entry.pos == 1 else cfg["primary_light"]
    acc_alpha = 255 if entry.pos <= 3 else 180
    acc_w  = stripe + slant
    accent = Image.new("RGBA", (acc_w, bar_h), (0, 0, 0, 0))
    ImageDraw.Draw(accent).polygon([
        (slant, 0), (slant + stripe - 1, 0),
        (stripe - 1, bar_h - 1), (0, bar_h - 1),
    ], fill=(*acc_color, acc_alpha))
    img.paste(accent, (x, y), accent)

    draw = ImageDraw.Draw(img)

    # ── Position number — Bebas Neue (bigger, more impactful) ──────────────────
    f_pos  = font("title", int(h * 0.68))
    bb     = draw.textbbox((0, 0), str(entry.pos), font=f_pos)
    pw, ph = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(
        (x + slant + stripe + (pos_w - stripe - pw) // 2 - bb[0],
         y + (bar_h - ph) // 2 - bb[1]),
        str(entry.pos), font=f_pos, fill=(255, 255, 255),
    )

    # ── Pre-compute time position ──────────────────────────────────────────────
    f_time  = font("bold", int(h * 0.33))
    bb_t    = draw.textbbox((0, 0), entry.time, font=f_time)
    time_tw = bb_t[2] - bb_t[0]
    time_th = bb_t[3] - bb_t[1]
    time_x  = x + w - slant - time_tw - int(16 * scale)

    # ── Name ──────────────────────────────────────────────────────────────────
    f_name     = font("bold", int(h * 0.32))
    name_x     = x + pos_w + slant + int(14 * scale)
    max_name_w = time_x - name_x - int(18 * scale)
    name_str   = entry.name
    while True:
        bb = draw.textbbox((0, 0), name_str, font=f_name)
        if (bb[2] - bb[0]) <= max_name_w or len(name_str) < 4:
            break
        name_str = name_str[:-1]
    if name_str != entry.name:
        name_str = name_str.rstrip() + "…"
    bb_name = draw.textbbox((0, 0), name_str, font=f_name)
    draw.text(
        (name_x, y + (bar_h - (bb_name[3] - bb_name[1])) // 2 - bb_name[1]),
        name_str, font=f_name, fill=text_c,
    )

    # ── Dot leader (fills wide gap — TV / landscape) ─────────────────────────
    leader_x1 = name_x + (bb_name[2] - bb_name[0]) + int(12 * scale)
    leader_x2 = time_x - int(12 * scale)
    if leader_x2 > leader_x1 + int(30 * scale):
        dot_c    = _lerp_color(text_c, bar_r, 0.60)
        dot_r    = max(1, int(2 * scale))
        dot_step = max(8, int(14 * scale))
        dot_y    = y + bar_h // 2
        for dx in range(int(leader_x1), int(leader_x2), dot_step):
            draw.ellipse([dx, dot_y - dot_r, dx + dot_r * 2, dot_y + dot_r],
                         fill=dot_c)

    # ── Time — primary_light on dark rows, white on hero row ──────────────────
    time_c = (255, 255, 255) if entry.pos == 1 else cfg["primary_light"]
    draw.text(
        (time_x, y + (bar_h - time_th) // 2 - bb_t[1]),
        entry.time, font=f_time, fill=time_c,
    )


# ─── Cover Slide ───────────────────────────────────────────────────────────────

def _dark_bg(cfg: dict, size: tuple) -> Image.Image:
    """Dark track-color background with radial depth and halftone dots — brand style."""
    W, H = size
    # Base gradient: bg → primary_dark (top darker, center slightly lighter)
    img  = _vertical_gradient(size,
                               _lerp_color(cfg["bg"], (0,0,0), 0.25),
                               _lerp_color(cfg["bg"], cfg["primary"], 0.30))
    # Radial glow at center for photo-like depth
    img  = _add_radial_glow(img, W//2, int(H*0.42), int(min(W,H)*0.88),
                             cfg["primary"], max_alpha=55)
    img  = _add_radial_glow(img, W//2, int(H*0.30), int(min(W,H)*0.40),
                             cfg["primary_light"], max_alpha=20)
    # Halftone dot texture (brand signature)
    img  = _add_halftone(img, step=14, dot_r=3, max_alpha=20)
    return img


def gen_cover(track: Track, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    is_tv = W > H
    scale = H / 1080 if is_tv else min(W / 1080, H / 1350)

    img  = _dark_bg(cfg, size)
    draw = ImageDraw.Draw(img)

    if is_tv:
        # ── TV Cover ──────────────────────────────────────────────────────────
        # Logo centered in top 35%
        _place_logo_white(img, int(H * 0.26), int(H * 0.55), int(H * 0.28))
        draw = ImageDraw.Draw(img)

        # "RANKING" centered
        f_r = font("title", int(195 * scale))
        center_text(draw, int(H * 0.40), "RANKING", f_r, (255, 255, 255), W)

        # "DA SEMANA" in primary_light
        f_s = font("title", int(120 * scale))
        center_text(draw, int(H * 0.60), "DA SEMANA", f_s, cfg["primary_light"], W)

        # Period + track name
        if track.period_start and track.period_end:
            f_p = font("bold", int(28 * scale))
            period_str = f"{track.period_start} ATÉ {track.period_end}"
            center_text(draw, int(H * 0.80), period_str, f_p, (220, 220, 230), W)

        f_t = font("bold", int(36 * scale))
        center_text(draw, int(H * 0.88), cfg["name"], f_t, cfg["primary_light"], W)

    else:
        # ── Instagram Cover — exact match to brand production style ───────────
        # Logo centered in top 30%
        _place_logo_white(img, int(H * 0.22), int(W * 0.62), int(H * 0.20))
        draw = ImageDraw.Draw(img)

        # "RANKING" — white, massive
        f_r = font("title", int(205 * scale))
        center_text(draw, int(H * 0.385), "RANKING", f_r, (255, 255, 255), W)

        # "DA SEMANA" — primary_light, slightly smaller
        f_s = font("title", int(130 * scale))
        center_text(draw, int(H * 0.534), "DA SEMANA", f_s, cfg["primary_light"], W)

        # Period: "25/05/2026 ATÉ 31/05/2026" — white semibold
        if track.period_start and track.period_end:
            f_p = font("semibold", int(34 * scale))
            period_str = f"{track.period_start} ATÉ {track.period_end}"
            center_text(draw, int(H * 0.698), period_str, f_p, (255, 255, 255), W)

        # Track name — bold white centered
        f_t = font("bold", int(46 * scale))
        center_text(draw, int(H * 0.775), cfg["name"], f_t, cfg["primary_light"], W)

    return img


# ─── TV Ranking Layout (1920×1080) ─────────────────────────────────────────────

def _gen_ranking_tv(track: Track, cat: Category, cfg: dict, W: int, H: int) -> Image.Image:
    s = H / 1080

    # ── Background: dark track color + halftone ───────────────────────────────
    img  = _dark_bg(cfg, (W, H))
    draw = ImageDraw.Draw(img)

    # ── Left sidebar darker overlay ────────────────────────────────────────────
    panel_w = int(272 * s)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(panel_w + int(40 * s)):
        t = x / (panel_w + int(40 * s))
        a = int(90 * (1 - t ** 1.2))
        for y in range(H):
            ov.putpixel((x, y), (0, 0, 0, a))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── Top accent bar ─────────────────────────────────────────────────────────
    bar_th = max(10, int(12 * s))
    draw.rectangle([0, 0, W, bar_th], fill=cfg["primary_light"])

    # ── Sidebar: white logo + track name + period ──────────────────────────────
    _place_logo_white(img, int(H * 0.20), int(panel_w * 0.80), int(panel_w * 0.32),
                      container_w=panel_w)
    draw = ImageDraw.Draw(img)

    f_trk = font("title", int(58 * s))
    trk_lines = cfg["name"].split()
    ty = int(H * 0.40)
    for line in trk_lines:
        bb  = draw.textbbox((0, 0), line, font=f_trk)
        lx  = (panel_w - (bb[2] - bb[0])) // 2 - bb[0]
        draw.text((lx, ty), line, font=f_trk, fill=(255, 255, 255))
        ty += int((bb[3] - bb[1]) * 1.08)

    if track.period_start and track.period_end:
        f_per = font("regular", int(15 * s))
        for i, ps in enumerate([track.period_start, track.period_end]):
            bb  = draw.textbbox((0, 0), ps, font=f_per)
            lx  = (panel_w - (bb[2] - bb[0])) // 2 - bb[0]
            draw.text((lx, int(H * 0.73) + i * int(20 * s)), ps,
                      font=f_per, fill=(220, 220, 240))

    # ── Content area ──────────────────────────────────────────────────────────
    cx    = panel_w + int(40 * s) + int(32 * s)
    cw    = W - cx - int(36 * s)

    # Header: title + category pill
    f_title = font("title", int(64 * s))
    draw.text((cx, bar_th + int(6 * s)), "RANKING DA SEMANA",
              font=f_title, fill=(255, 255, 255))

    f_cat  = font("bold", int(24 * s))
    c_lbl  = cat.label.upper()
    bb     = draw.textbbox((0, 0), c_lbl, font=f_cat)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(22 * s), int(9 * s)
    pill_w = tw + px_ * 2
    pill_h = th + py_ * 2
    pill_x = W - pill_w - int(36 * s)
    pill_y = bar_th + int(8 * s)
    pill   = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill_w-1, pill_h-1],
                                           radius=pill_h//2,
                                           fill=(*cfg["primary"], 255))
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              c_lbl, font=f_cat, fill=(255, 255, 255))

    # Header separator
    hdr_h  = int(74 * s)
    sep_y  = bar_th + hdr_h
    sep_th = max(2, int(3 * s))
    draw.rectangle([cx, sep_y, W - int(36 * s), sep_y + sep_th], fill=cfg["primary"])

    # Column labels
    row_h  = int(84 * s)
    row_h1 = int(row_h * 1.12)
    row_g  = int(5 * s)
    lbl_y  = sep_y + sep_th + int(6 * s)
    f_lbl  = font("regular", int(16 * s))
    lbl_col = (180, 180, 200)
    slant_r = int(row_h * 0.16)
    pos_r   = int(row_h * 0.88)
    draw.text((cx + pos_r + slant_r + int(14 * s), lbl_y),
              "COMPETIDOR", font=f_lbl, fill=lbl_col)
    bb_lbl = draw.textbbox((0, 0), "TEMPO", font=f_lbl)
    draw.text((W - int(36 * s) - slant_r - (bb_lbl[2]-bb_lbl[0]) - int(16*s), lbl_y),
              "TEMPO", font=f_lbl, fill=lbl_col)

    # Rows
    start_y  = lbl_y + int(f_lbl.size) + int(8 * s)
    y_cursor = start_y

    for entry in cat.entries:
        rh = row_h1 if entry.pos == 1 else row_h
        if entry.pos == 4:
            pd_y = y_cursor - row_g // 2
            draw.line([(cx, pd_y), (W - int(36*s), pd_y)],
                      fill=(*cfg["primary"], 60), width=max(1, int(1*s)))
        if entry.pos == 1:
            img = _add_radial_glow(img, cx + int(cw * 0.5), y_cursor + rh // 2,
                                   int(rh * 2.8), cfg["primary_light"], max_alpha=18)
        _draw_row(img, draw, cx, y_cursor, cw, rh, entry, cfg, s)
        draw = ImageDraw.Draw(img)
        y_cursor += rh + row_g

    # Bottom accent bar
    draw.rectangle([0, H - max(7, int(7 * s)), W, H], fill=cfg["primary"])

    return img


# ─── Ranking Slide (Instagram portrait) ────────────────────────────────────────

def gen_ranking(track: Track, cat: Category, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    if W > H:
        return _gen_ranking_tv(track, cat, cfg, W, H)

    scale = min(W / 1080, H / 1350)

    # ── Background: dark track color + halftone (same as cover) ───────────────
    img  = _dark_bg(cfg, (W, H))
    draw = ImageDraw.Draw(img)

    # ── Top accent bar ─────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, max(10, int(12 * scale))], fill=cfg["primary_light"])

    # ── Header ─────────────────────────────────────────────────────────────────
    # "RANKING DA SEMANA" — white title
    f_title = font("title", int(80 * scale))
    center_text(draw, int(20 * scale), "RANKING DA SEMANA",
                f_title, (255, 255, 255), W)

    # Category pill — primary_light fill
    f_cat  = font("bold", int(26 * scale))
    c_lbl  = cat.label.upper()
    bb     = draw.textbbox((0, 0), c_lbl, font=f_cat)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(30 * scale), int(11 * scale)
    pill_w = tw + px_ * 2
    pill_h = th + py_ * 2
    pill_x = (W - pill_w) // 2
    pill_y = int(H * 0.108)
    pill   = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill_w-1, pill_h-1],
                                           radius=pill_h//2,
                                           fill=(*cfg["primary_light"], 240))
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              c_lbl, font=f_cat, fill=_text_on(cfg["primary_light"]))

    # ── Separator ─────────────────────────────────────────────────────────────
    sep_y  = pill_y + pill_h + int(14 * scale)
    sep_th = max(2, int(2 * scale))
    draw.rectangle([int(52 * scale), sep_y, W - int(52 * scale), sep_y + sep_th],
                   fill=(*cfg["primary_light"], 100))

    # ── Column labels ─────────────────────────────────────────────────────────
    f_lbl   = font("regular", int(17 * scale))
    row_m   = int(44 * scale)
    row_w   = W - row_m * 2
    lbl_y   = sep_y + sep_th + int(10 * scale)
    lbl_col = (180, 180, 200)
    slant_r = int(int(84 * scale) * 0.16)
    pos_r   = int(int(84 * scale) * 0.88)
    draw.text((row_m + pos_r + slant_r + int(14 * scale), lbl_y),
              "COMPETIDOR", font=f_lbl, fill=lbl_col)
    bb_t = draw.textbbox((0, 0), "TEMPO", font=f_lbl)
    draw.text((row_m + row_w - slant_r - (bb_t[2]-bb_t[0]) - int(16*scale), lbl_y),
              "TEMPO", font=f_lbl, fill=lbl_col)

    # ── Rows ──────────────────────────────────────────────────────────────────
    row_h_base = int(84 * scale)
    row_h_1    = int(row_h_base * 1.14)
    row_g      = int(5 * scale)
    start_y    = lbl_y + int(f_lbl.size) + int(9 * scale)

    y_cursor = start_y
    for entry in cat.entries:
        rh = row_h_1 if entry.pos == 1 else row_h_base
        if entry.pos == 4:
            pd_y = y_cursor - row_g // 2
            draw.line([(row_m, pd_y), (row_m + row_w, pd_y)],
                      fill=(*cfg["primary_light"], 50), width=max(1, int(1 * scale)))
        if entry.pos == 1:
            img = _add_radial_glow(img, W // 2, y_cursor + rh // 2,
                                   int(rh * 3.5), cfg["primary_light"], max_alpha=22)
        _draw_row(img, draw, row_m, y_cursor, row_w, rh, entry, cfg, scale)
        draw = ImageDraw.Draw(img)
        y_cursor += rh + row_g

    # ── Footer: logo branca ────────────────────────────────────────────────────
    footer_y   = y_cursor + int(10 * scale)
    footer_mid = footer_y + (H - footer_y) // 2
    _place_logo_white(img, footer_mid, int(240 * scale), int(70 * scale))

    return img


# ─── Orchestration ─────────────────────────────────────────────────────────────

def generate_all(tracks_data: List[Track], period_override: Optional[str] = None) -> None:
    OUT_IG.mkdir(parents=True, exist_ok=True)
    OUT_TV.mkdir(parents=True, exist_ok=True)

    # Determine shared period across all tracks
    all_starts, all_ends = [], []
    for t in tracks_data:
        if t.period_start:
            all_starts.append(datetime.strptime(t.period_start, "%d/%m/%Y"))
        if t.period_end:
            all_ends.append(datetime.strptime(t.period_end, "%d/%m/%Y"))

    global_start = min(all_starts).strftime("%d/%m/%Y") if all_starts else ""
    global_end   = max(all_ends).strftime("%d/%m/%Y")   if all_ends   else ""

    if period_override:
        parts = re.split(r'\s+a\s+', period_override, flags=re.IGNORECASE)
        if len(parts) == 2:
            global_start, global_end = parts[0].strip(), parts[1].strip()

    for track in tracks_data:
        track.period_start = global_start
        track.period_end   = global_end

    for track in tracks_data:
        cfg = TRACKS[track.key]
        track_slug = track.key

        print(f"\n→ {cfg['name']} ({len(track.categories)} categorias, "
              f"{global_start} a {global_end})")

        for fmt_name, size, out_dir in [
            ("instagram", (1080, 1350), OUT_IG),
            ("tv",        (1920, 1080), OUT_TV),
        ]:
            subdir = out_dir / track_slug
            subdir.mkdir(exist_ok=True)

            # Cover
            cover = gen_cover(track, cfg, size)
            cover_path = subdir / "01_capa.png"
            cover.save(cover_path)
            print(f"  [{fmt_name}] {cover_path.name}")

            # Rankings
            for i, cat in enumerate(track.categories, 2):
                slide = gen_ranking(track, cat, cfg, size)
                slug  = cat.label.lower().replace(" ", "_").replace("/", "_")
                path  = subdir / f"{i:02d}_{slug}.png"
                slide.save(path)
                print(f"  [{fmt_name}] {path.name}")

    print("\nConcluído! Arquivos em:")
    print(f"  Instagram: {OUT_IG}")
    print(f"  TV:        {OUT_TV}")


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Gera imagens de ranking semanal do MetaKart"
    )
    p.add_argument("--barra",        required=True, help="PDF da pista Barra")
    p.add_argument("--norte",        required=True, help="PDF da pista Norte")
    p.add_argument("--campo-grande", required=True, help="PDF da pista Campo Grande")
    p.add_argument("--period",       default=None,
                   help='Período manual, ex: "25/05/2026 a 31/05/2026"')
    args = p.parse_args()

    tracks_data = []
    for key, path in [
        ("barra",        args.barra),
        ("norte",        args.norte),
        ("campo_grande", args.campo_grande),
    ]:
        print(f"Lendo {key}: {path} ...", end=" ", flush=True)
        try:
            track = parse_pdf(path, key)
            print(f"OK ({sum(len(c.entries) for c in track.categories)} entradas)")
            if not track.categories:
                print(f"  AVISO: nenhuma categoria encontrada em {path}")
            tracks_data.append(track)
        except Exception as e:
            print(f"ERRO: {e}")
            sys.exit(1)

    generate_all(tracks_data, period_override=args.period)


if __name__ == "__main__":
    main()
