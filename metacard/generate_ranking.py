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
OUT_IG   = BASE_DIR / "output" / "instagram"
OUT_TV   = BASE_DIR / "output" / "tv"

# ─── Track Config ──────────────────────────────────────────────────────────────

TRACKS = {
    "barra": {
        "name":          "BARRA",
        "primary":       (108,  52, 200),
        "primary_dark":  ( 58,  22, 120),
        "primary_light": (168, 110, 255),
        "bg":            (248, 247, 252),   # near-white, slight violet tint
        "row_bg":        (237, 230, 252),   # very light violet for podium rows
        "num_bg":        (108,  52, 200),   # same as primary for pos badge
    },
    "norte": {
        "name":          "NORTE",
        "primary":       ( 22, 150,  48),
        "primary_dark":  ( 10,  80,  22),
        "primary_light": ( 60, 210,  90),
        "bg":            (247, 252, 248),   # near-white, slight green tint
        "row_bg":        (224, 248, 228),   # very light green for podium rows
        "num_bg":        ( 22, 150,  48),
    },
    "campo_grande": {
        "name":          "CAMPO GRANDE",
        "primary":       (240,  98,   0),
        "primary_dark":  (160,  55,   0),
        "primary_light": (255, 165,  50),
        "bg":            (252, 248, 244),   # near-white, warm tint
        "row_bg":        (255, 237, 212),   # very light orange for podium rows
        "num_bg":        (240,  98,   0),
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
    if _lum(bg) > 0.45:
        return (28, 28, 35)
    return (255, 255, 255)


def _row_palette(pos: int, cfg: dict) -> Tuple[tuple, tuple, tuple]:
    """Light-bg style: podium rows use tinted fill, others near-white."""
    white = (255, 255, 255)
    if pos == 1:
        bar_l = cfg["row_bg"]
        bar_r = _lerp_color(cfg["row_bg"], white, 0.30)
        num_c = cfg["primary"]
    elif pos == 2:
        bar_l = _lerp_color(cfg["row_bg"], white, 0.20)
        bar_r = _lerp_color(cfg["row_bg"], white, 0.55)
        num_c = cfg["primary"]
    elif pos == 3:
        bar_l = _lerp_color(cfg["row_bg"], white, 0.45)
        bar_r = _lerp_color(cfg["row_bg"], white, 0.75)
        num_c = cfg["primary"]
    else:
        bar_l = (245, 245, 248)
        bar_r = white
        num_c = cfg["primary_dark"]
    return bar_l, bar_r, num_c


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


def _make_checker_faded(size: int, cell: int) -> Image.Image:
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    n    = size // cell + 2
    diag = (size ** 2 * 2) ** 0.5
    for r in range(n):
        for c in range(n):
            if (r + c) % 2 == 0:
                dist  = ((r * cell) ** 2 + (c * cell) ** 2) ** 0.5
                alpha = int(120 * max(0.0, 1.0 - (dist / diag) * 1.5) ** 1.5)
                if alpha > 4:
                    x1, y1 = c * cell, r * cell
                    draw.rectangle([x1, y1, x1 + cell - 1, y1 + cell - 1],
                                   fill=(255, 255, 255, alpha))
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
    gap    = int(4 * scale)
    bar_h  = h - gap
    pos_w  = int(h * 0.90)
    slant  = int(bar_h * 0.16)
    stripe = max(5, int(5 * scale))

    bar_l, bar_r, num_c = _row_palette(entry.pos, cfg)

    # ── Row gradient (parallelogram) ───────────────────────────────────────────
    grad = _gradient_bar(w, bar_h, bar_l, bar_r).convert("RGBA")
    shine_h = max(3, bar_h // 5)
    for sy in range(shine_h):
        a = int(40 * (1.0 - sy / shine_h) ** 1.5)
        ImageDraw.Draw(grad).line([(0, sy), (w - 1, sy)], fill=(255, 255, 255, a))
    grad.putalpha(_para_mask(w, bar_h, slant))
    img.paste(grad, (x, y), grad)

    # ── Position badge (left parallelogram) ────────────────────────────────────
    badge_w = pos_w + slant
    badge   = Image.new("RGBA", (badge_w, bar_h), (*num_c, 240))
    badge.putalpha(_para_mask(badge_w, bar_h, slant))
    img.paste(badge, (x, y), badge)

    # ── Left accent stripe (diagonal) ──────────────────────────────────────────
    acc_w  = stripe + slant
    accent = Image.new("RGBA", (acc_w, bar_h), (0, 0, 0, 0))
    ImageDraw.Draw(accent).polygon([
        (slant, 0), (slant + stripe - 1, 0),
        (stripe - 1, bar_h - 1), (0, bar_h - 1),
    ], fill=(*cfg["primary_light"], 255))
    img.paste(accent, (x, y), accent)

    draw = ImageDraw.Draw(img)

    # ── Separator between badge and name area ──────────────────────────────────
    sep_x = x + pos_w + slant
    draw.line(
        [(sep_x, y + int(bar_h * 0.18)), (sep_x, y + int(bar_h * 0.82))],
        fill=(*cfg["primary_light"], 55), width=1,
    )

    # ── Position number (adaptive text color) ──────────────────────────────────
    f_pos  = font("bold", int(h * 0.44))
    bb     = draw.textbbox((0, 0), str(entry.pos), font=f_pos)
    pw, ph = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(
        (x + slant + stripe + (pos_w - stripe - pw) // 2 - bb[0],
         y + (bar_h - ph) // 2 - bb[1]),
        str(entry.pos), font=f_pos, fill=_text_on(num_c),
    )

    # ── Pre-compute time position (needed for dot leader) ──────────────────────
    f_time  = font("semibold", int(h * 0.305))
    bb_t    = draw.textbbox((0, 0), entry.time, font=f_time)
    time_tw = bb_t[2] - bb_t[0]
    time_th = bb_t[3] - bb_t[1]
    time_x  = x + w - slant - time_tw - int(14 * scale)

    # ── Name (adaptive text color) ─────────────────────────────────────────────
    f_name     = font("bold", int(h * 0.295))
    name_x     = x + pos_w + slant + int(12 * scale)
    max_name_w = time_x - name_x - int(16 * scale)
    name_str   = entry.name
    while True:
        bb = draw.textbbox((0, 0), name_str, font=f_name)
        if (bb[2] - bb[0]) <= max_name_w or len(name_str) < 4:
            break
        name_str = name_str[:-1]
    if name_str != entry.name:
        name_str = name_str.rstrip() + "…"
    bb_name = draw.textbbox((0, 0), name_str, font=f_name)
    name_mid_c = _lerp_color(bar_l, bar_r, (name_x - x) / max(w - 1, 1))
    draw.text(
        (name_x, y + (bar_h - (bb_name[3] - bb_name[1])) // 2 - bb_name[1]),
        name_str, font=f_name, fill=_text_on(name_mid_c),
    )

    # ── Dot leader between name and time (fills gap on TV) ────────────────────
    leader_x1 = name_x + (bb_name[2] - bb_name[0]) + int(10 * scale)
    leader_x2 = time_x - int(10 * scale)
    if leader_x2 > leader_x1 + int(28 * scale):
        dot_r    = max(1, int(2 * scale))
        dot_step = max(7, int(13 * scale))
        dot_y    = y + bar_h // 2
        for dx in range(int(leader_x1), int(leader_x2), dot_step):
            t  = (dx - x) / max(w - 1, 1)
            dc = _lerp_color(_lerp_color(bar_l, bar_r, t), (255, 255, 255), 0.28)
            draw.ellipse([dx, dot_y - dot_r, dx + dot_r * 2, dot_y + dot_r],
                         fill=dc)

    # ── Time (adaptive text color) ─────────────────────────────────────────────
    time_mid_c = _lerp_color(bar_l, bar_r, (time_x - x) / max(w - 1, 1))
    draw.text(
        (time_x, y + (bar_h - time_th) // 2 - bb_t[1]),
        entry.time, font=f_time, fill=_text_on(time_mid_c),
    )


# ─── Cover Slide ───────────────────────────────────────────────────────────────

def gen_cover(track: Track, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    scale = H / 1080 if W > H else min(W / 1080, H / 1350)

    # ── Background: white with thick color band at top ─────────────────────────
    img  = Image.new("RGB", size, cfg["bg"])
    draw = ImageDraw.Draw(img)

    # Top color block — ~38% of height for portrait, ~55% for landscape
    block_h = int(H * (0.55 if W > H else 0.42))
    # Gradient: primary → primary_dark downward in the color block
    for y in range(block_h):
        t = y / max(block_h - 1, 1)
        draw.line([(0, y), (W, y)], fill=_lerp_color(cfg["primary"], cfg["primary_dark"], t))

    # Diagonal cut between color block and white — parallelogram edge
    cut_h = int(80 * scale)
    cut_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # Fill the triangle that "cuts" into the white area
    ImageDraw.Draw(cut_overlay).polygon([
        (0, block_h - cut_h), (W, block_h),
        (W, block_h + cut_h), (0, block_h),
    ], fill=(*cfg["primary_dark"], 255))
    img = Image.alpha_composite(img.convert("RGBA"), cut_overlay).convert("RGB")

    # Cover the area below the cut with white bg
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, block_h + cut_h, W, H], fill=cfg["bg"])

    # Re-draw the diagonal cut cleanly
    cut2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cut2).polygon([
        (0, block_h - cut_h), (W, block_h - cut_h // 2),
        (W, block_h + cut_h), (0, block_h + cut_h),
    ], fill=(*cfg["primary"], 255))
    img = Image.alpha_composite(img.convert("RGBA"), cut2).convert("RGB")

    # Checkered pattern — top-right corner of color block
    flag_sz = int(280 * scale)
    checker = _make_checker_faded(flag_sz, int(32 * scale))
    # Make it dark-on-dark (use black checker on color bg)
    checker_dark = Image.new("RGBA", checker.size, (0, 0, 0, 0))
    for py in range(checker.height):
        for px2 in range(checker.width):
            r, g, b, a = checker.getpixel((px2, py))
            checker_dark.putpixel((px2, py), (0, 0, 0, a // 2))
    img.paste(checker_dark, (W - flag_sz + int(10 * scale), -int(10 * scale)), checker_dark)

    draw = ImageDraw.Draw(img)

    # ── Top accent stripe ──────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, max(8, int(10 * scale))], fill=cfg["primary_light"])

    # ── Logo (in the white area or just below cut) ─────────────────────────────
    logo_y = int(H * (0.64 if W > H else 0.60))
    _place_logo(img, logo_y, int(380 * scale), int(160 * scale))
    draw = ImageDraw.Draw(img)

    # ── "RANKING" in the color block ───────────────────────────────────────────
    f_r = font("title", int(195 * scale))
    center_text(draw, int(H * 0.12), "RANKING", f_r, (255, 255, 255), W, shadow=False)

    # ── "DA SEMANA" below it ───────────────────────────────────────────────────
    f_s = font("title", int(120 * scale))
    center_text(draw, int(H * 0.30), "DA SEMANA", f_s, cfg["primary_light"], W, shadow=False)

    # ── Track name pill — in the white area, below logo ────────────────────────
    f_t      = font("bold", int(46 * scale))
    bb       = draw.textbbox((0, 0), cfg["name"], font=f_t)
    tw, th   = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(34 * scale), int(12 * scale)
    pill_w   = tw + px_ * 2
    pill_h   = th + py_ * 2
    pill_x   = (W - pill_w) // 2
    pill_y   = int(H * 0.75)
    pill     = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle(
        [0, 0, pill_w - 1, pill_h - 1], radius=pill_h // 2,
        fill=(*cfg["primary"], 255),
    )
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              cfg["name"], font=f_t, fill=(255, 255, 255))

    # ── Period line ────────────────────────────────────────────────────────────
    if track.period_start and track.period_end:
        f_p = font("regular", int(28 * scale))
        center_text(draw, int(H * 0.86),
                    f"{track.period_start}  ·  {track.period_end}",
                    f_p, (100, 100, 110), W)

    # ── Bottom accent bar ──────────────────────────────────────────────────────
    draw.rectangle([0, H - max(6, int(8 * scale)), W, H], fill=cfg["primary"])

    return img


# ─── TV Ranking Layout (1920×1080) ─────────────────────────────────────────────

def _gen_ranking_tv(track: Track, cat: Category, cfg: dict, W: int, H: int) -> Image.Image:
    s = H / 1080

    # ── Background: white with color left panel ────────────────────────────────
    img  = Image.new("RGB", (W, H), cfg["bg"])

    # Left color panel (~22% width)
    panel_w = int(W * 0.22)
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(panel_w + int(60 * s)):
        t = x / (panel_w + int(60 * s))
        alpha = int(255 * (1 - t ** 1.5))
        for y in range(H):
            panel.putpixel((x, y), (*cfg["primary"], alpha))
    img = Image.alpha_composite(img.convert("RGBA"), panel).convert("RGB")

    # Diagonal edge on the panel
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).polygon([
        (panel_w - int(40*s), 0),
        (panel_w + int(40*s), 0),
        (panel_w - int(20*s), H),
        (panel_w - int(100*s), H),
    ], fill=(*cfg["primary_dark"], 180))
    img = Image.alpha_composite(img.convert("RGBA"), edge).convert("RGB")

    # Checker — top of color panel
    flag_sz = int(200 * s)
    checker = _make_checker_faded(flag_sz, int(24 * s))
    ck_dark = Image.new("RGBA", checker.size, (0, 0, 0, 0))
    for py in range(checker.height):
        for px2 in range(checker.width):
            _, _, _, a = checker.getpixel((px2, py))
            ck_dark.putpixel((px2, py), (0, 0, 0, a // 2))
    img.paste(ck_dark, (0, 0), ck_dark)

    draw = ImageDraw.Draw(img)

    # ── Top accent bar ─────────────────────────────────────────────────────────
    bar_th = max(8, int(10 * s))
    draw.rectangle([0, 0, W, bar_th], fill=cfg["primary_light"])

    # ── Left panel content: logo + track name ──────────────────────────────────
    _place_logo(img, int(H * 0.22), int(panel_w * 0.75), int(panel_w * 0.30))
    draw = ImageDraw.Draw(img)

    f_trk = font("title", int(52 * s))
    trk_lines = cfg["name"].split()
    ty = int(H * 0.42)
    for line in trk_lines:
        bb = draw.textbbox((0, 0), line, font=f_trk)
        lx = (panel_w - (bb[2] - bb[0])) // 2 - bb[0]
        draw.text((lx, ty), line, font=f_trk, fill=(255, 255, 255))
        ty += int((bb[3] - bb[1]) * 1.1)

    # Period on left panel
    if track.period_start and track.period_end:
        f_per = font("regular", int(15 * s))
        per_str = f"{track.period_start}"
        per_str2 = f"{track.period_end}"
        for i, ps in enumerate([per_str, per_str2]):
            bb = draw.textbbox((0, 0), ps, font=f_per)
            lx = (panel_w - (bb[2] - bb[0])) // 2 - bb[0]
            draw.text((lx, int(H * 0.72) + i * int(20 * s)), ps,
                      font=f_per, fill=(255, 255, 200))

    # ── Main content area: header ──────────────────────────────────────────────
    content_x = panel_w + int(50 * s)
    content_w = W - content_x - int(40 * s)
    hdr_h     = int(72 * s)

    f_title = font("title", int(62 * s))
    draw.text((content_x, bar_th + int(8 * s)), "RANKING DA SEMANA",
              font=f_title, fill=cfg["primary"])

    # Category pill
    f_cat  = font("bold", int(26 * s))
    c_lbl  = cat.label.upper()
    bb     = draw.textbbox((0, 0), c_lbl, font=f_cat)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(24 * s), int(10 * s)
    pill_w = tw + px_ * 2
    pill_h = th + py_ * 2
    pill_x = W - pill_w - int(40 * s)
    pill_y = bar_th + int(8 * s)
    pill   = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill_w - 1, pill_h - 1],
                                           radius=pill_h // 2,
                                           fill=(*cfg["primary"], 255))
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]), c_lbl,
              font=f_cat, fill=(255, 255, 255))

    # Header separator
    sep_y  = bar_th + hdr_h
    sep_th = max(2, int(3 * s))
    draw.rectangle([content_x, sep_y, W, sep_y + sep_th], fill=cfg["primary"])

    # ── Column labels ──────────────────────────────────────────────────────────
    row_h  = int(82 * s)
    row_h1 = int(row_h * 1.10)
    row_g  = int(6 * s)
    lbl_y  = sep_y + sep_th + int(8 * s)
    f_lbl  = font("regular", int(17 * s))
    lbl_col = (130, 130, 140)
    slant_r = int(row_h * 0.16)
    pos_w_r = int(row_h * 0.90)
    draw.text((content_x + pos_w_r + slant_r + int(12 * s), lbl_y),
              "COMPETIDOR", font=f_lbl, fill=lbl_col)
    bb_lbl = draw.textbbox((0, 0), "TEMPO", font=f_lbl)
    draw.text((W - int(40 * s) - slant_r - (bb_lbl[2] - bb_lbl[0]) - int(14 * s), lbl_y),
              "TEMPO", font=f_lbl, fill=lbl_col)

    # ── Rows ──────────────────────────────────────────────────────────────────
    start_y  = lbl_y + int(f_lbl.size) + int(8 * s)
    y_cursor = start_y

    for entry in cat.entries:
        rh = row_h1 if entry.pos == 1 else row_h
        if entry.pos == 4:
            pd_y = y_cursor - row_g // 2
            draw.line([(content_x, pd_y), (W - int(40*s), pd_y)],
                      fill=(*cfg["primary"], 80), width=max(1, int(1 * s)))
        _draw_row(img, draw, content_x, y_cursor, content_w, rh, entry, cfg, s)
        draw = ImageDraw.Draw(img)
        y_cursor += rh + row_g

    # Bottom accent bar
    draw.rectangle([0, H - max(6, int(6 * s)), W, H], fill=cfg["primary"])

    return img


# ─── Ranking Slide (Instagram portrait) ────────────────────────────────────────

def gen_ranking(track: Track, cat: Category, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    if W > H:
        return _gen_ranking_tv(track, cat, cfg, W, H)

    scale = min(W / 1080, H / 1350)

    # ── Background: white ─────────────────────────────────────────────────────
    img  = Image.new("RGB", (W, H), cfg["bg"])
    draw = ImageDraw.Draw(img)

    # Top color header block
    hdr_block_h = int(220 * scale)
    for y in range(hdr_block_h):
        t = y / max(hdr_block_h - 1, 1)
        draw.line([(0, y), (W, y)], fill=_lerp_color(cfg["primary"], cfg["primary_dark"], t))

    # Diagonal cut
    cut_h = int(55 * scale)
    cut_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cut_ov).polygon([
        (0, hdr_block_h - cut_h), (W, hdr_block_h + cut_h // 2),
        (W, hdr_block_h + cut_h), (0, hdr_block_h),
    ], fill=(*cfg["primary_dark"], 255))
    img = Image.alpha_composite(img.convert("RGBA"), cut_ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    # Fill white below cut
    draw.rectangle([0, hdr_block_h + cut_h, W, H], fill=cfg["bg"])

    # ── Top accent stripe ──────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, max(8, int(10 * scale))], fill=cfg["primary_light"])

    # Checker top-right (dark on color bg)
    flag_sz = int(200 * scale)
    checker = _make_checker_faded(flag_sz, int(22 * scale))
    ck_dark = Image.new("RGBA", checker.size, (0, 0, 0, 0))
    for py in range(checker.height):
        for px2 in range(checker.width):
            _, _, _, a = checker.getpixel((px2, py))
            ck_dark.putpixel((px2, py), (0, 0, 0, a // 2))
    img.paste(ck_dark, (W - flag_sz + int(10 * scale), 0), ck_dark)
    draw = ImageDraw.Draw(img)

    # ── Header text ───────────────────────────────────────────────────────────
    f_title = font("title", int(90 * scale))
    center_text(draw, int(20 * scale), "RANKING", f_title, (255, 255, 255), W)

    f_sub = font("title", int(54 * scale))
    center_text(draw, int(112 * scale), "DA SEMANA", f_sub, cfg["primary_light"], W)

    # ── Separator line under header ───────────────────────────────────────────
    sep_y  = hdr_block_h + cut_h + int(12 * scale)
    sep_th = max(2, int(2 * scale))
    draw.rectangle([int(60 * scale), sep_y, W - int(60 * scale), sep_y + sep_th],
                   fill=cfg["primary"])

    # ── Category pill ─────────────────────────────────────────────────────────
    f_cat  = font("bold", int(26 * scale))
    c_lbl  = cat.label.upper()
    bb     = draw.textbbox((0, 0), c_lbl, font=f_cat)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(28 * scale), int(12 * scale)
    pill_w = tw + px_ * 2
    pill_h = th + py_ * 2
    pill_x = (W - pill_w) // 2
    pill_y = sep_y + sep_th + int(14 * scale)
    pill   = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle(
        [0, 0, pill_w - 1, pill_h - 1], radius=pill_h // 2,
        fill=(*cfg["primary"], 255),
    )
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              c_lbl, font=f_cat, fill=(255, 255, 255))

    # ── Column labels ─────────────────────────────────────────────────────────
    f_lbl   = font("regular", int(18 * scale))
    row_m   = int(52 * scale)
    row_w   = W - row_m * 2
    slant   = int(int(80 * scale) * 0.16)
    lbl_y   = pill_y + pill_h + int(18 * scale)
    lbl_col = (140, 140, 150)
    draw.text((row_m + slant + int(12 * scale), lbl_y),
              "COMPETIDOR", font=f_lbl, fill=lbl_col)
    bb_t = draw.textbbox((0, 0), "TEMPO", font=f_lbl)
    draw.text((row_m + row_w - slant - (bb_t[2] - bb_t[0]) - int(14 * scale), lbl_y),
              "TEMPO", font=f_lbl, fill=lbl_col)

    # ── Rows ──────────────────────────────────────────────────────────────────
    row_h_base = int(80 * scale)
    row_h_1    = int(row_h_base * 1.12)
    row_g      = int(6 * scale)
    start_y    = lbl_y + int(f_lbl.size) + int(10 * scale)

    y_cursor = start_y
    for entry in cat.entries:
        rh = row_h_1 if entry.pos == 1 else row_h_base
        if entry.pos == 4:
            pd_y = y_cursor - row_g // 2
            draw.line([(row_m, pd_y), (row_m + row_w, pd_y)],
                      fill=(*cfg["primary"], 70), width=max(1, int(1 * scale)))
        _draw_row(img, draw, row_m, y_cursor, row_w, rh, entry, cfg, scale)
        draw = ImageDraw.Draw(img)
        y_cursor += rh + row_g

    # ── Track name + logo below rows ──────────────────────────────────────────
    bottom_area_y = y_cursor + int(12 * scale)
    bottom_center = bottom_area_y + (H - bottom_area_y) // 2

    f_trk = font("bold", int(22 * scale))
    bb = draw.textbbox((0, 0), cfg["name"], font=f_trk)
    trk_x = (W - (bb[2] - bb[0])) // 2 - bb[0]
    draw.text((trk_x, bottom_center - int(30 * scale) - (bb[3] - bb[1])),
              cfg["name"], font=f_trk, fill=cfg["primary"])

    _place_logo(img, bottom_center + int(18 * scale), int(240 * scale), int(60 * scale))

    draw = ImageDraw.Draw(img)

    # ── Bottom accent bar ─────────────────────────────────────────────────────
    draw.rectangle([0, H - max(6, int(8 * scale)), W, H], fill=cfg["primary"])

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
