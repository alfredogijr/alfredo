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
        "primary_dark":  ( 48,  20,  98),
        "primary_light": (162, 100, 248),
        "bg":            (  8,   4,  20),
        "row_bg":        ( 76,  34, 152),
        "num_bg":        ( 18,   8,  42),
    },
    "norte": {
        "name":          "NORTE",
        "primary":       ( 22, 130,  42),
        "primary_dark":  (  8,  52,  16),
        "primary_light": ( 44, 190,  72),
        "bg":            (  3,  10,   4),
        "row_bg":        ( 17,  98,  28),
        "num_bg":        (  5,  18,   8),
    },
    "campo_grande": {
        "name":          "CAMPO GRANDE",
        "primary":       (252, 108,   0),   # vivid orange
        "primary_dark":  ( 88,  30,   0),   # dark orange
        "primary_light": (255, 172,  45),   # bright warm orange
        "bg":            (152,  55,   0),   # ORANGE background — not dark
        "row_bg":        ( 62,  20,   0),   # dark rows for contrast on orange bg
        "num_bg":        ( 40,  13,   0),   # darkest number badge
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
        return (max(0, bg[0] // 7), max(0, bg[1] // 7), max(0, bg[2] // 7))
    return (255, 255, 255)


def _row_palette(pos: int, cfg: dict) -> Tuple[tuple, tuple, tuple]:
    """(bar_l, bar_r, num_c) using track-color tints for all positions."""
    if pos == 1:
        bar_l = _lerp_color(cfg["primary_light"], (255, 255, 255), 0.24)
        bar_r = cfg["primary_light"]
        num_c = cfg["primary"]
    elif pos == 2:
        bar_l = cfg["primary_light"]
        bar_r = cfg["primary"]
        num_c = _lerp_color(cfg["primary_dark"], cfg["primary"], 0.28)
    elif pos == 3:
        bar_l = cfg["primary"]
        bar_r = _lerp_color(cfg["primary"], cfg["row_bg"], 0.50)
        num_c = cfg["primary_dark"]
    else:
        bar_l = cfg["row_bg"]
        bar_r = _lerp_color(cfg["row_bg"], cfg["bg"], 0.44)
        num_c = cfg["num_bg"]
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
    scale = min(W / 1080, H / 1350)

    # Background: dark gradient (primary_dark → bg)
    img = _vertical_gradient(size, cfg["primary_dark"], cfg["bg"])

    # Radial glow — large soft center + tighter bright core
    img = _add_radial_glow(img, W // 2, int(H * 0.30),
                           int(min(W, H) * 0.82), cfg["primary"], max_alpha=58)
    img = _add_radial_glow(img, W // 2, int(H * 0.26),
                           int(min(W, H) * 0.28), cfg["primary_light"], max_alpha=30)

    # F1 livery: wide diagonal color band in background
    img = _add_diagonal_band(img, cfg["primary"],
                             y_left=0.54, y_right=0.30, thickness=0.24, alpha=30)

    # Faint track-name watermark (behind diagonal band)
    wm_img  = Image.new("RGBA", size, (0, 0, 0, 0))
    f_wm    = font("title", int(240 * scale))
    bb      = ImageDraw.Draw(wm_img).textbbox((0, 0), cfg["name"], font=f_wm)
    ImageDraw.Draw(wm_img).text(
        ((W - (bb[2] - bb[0])) // 2 - bb[0], int(H * 0.35)),
        cfg["name"], font=f_wm, fill=(*cfg["primary"], 14),
    )
    img = Image.alpha_composite(img.convert("RGBA"), wm_img).convert("RGB")

    # Faded checkered flag — bottom-right corner, rotated
    flag_sz = int(360 * scale)
    checker = _make_checker_faded(flag_sz, int(36 * scale)).rotate(180)
    img.paste(checker, (W - flag_sz + int(20 * scale), H - flag_sz + int(20 * scale)), checker)

    draw = ImageDraw.Draw(img)

    # Top accent bar + bottom thin line
    bar_thick = max(8, int(10 * scale))
    draw.rectangle([0, 0, W, bar_thick], fill=cfg["primary_light"])
    draw.rectangle([0, H - max(3, int(3 * scale)), W, H], fill=cfg["primary"])

    # Logo
    _place_logo(img, int(288 * scale), int(460 * scale), int(195 * scale))
    draw = ImageDraw.Draw(img)

    # "RANKING" — hero title
    f_r = font("title", int(182 * scale))
    center_text(draw, int(544 * scale), "RANKING", f_r, (255, 255, 255), W, shadow=True)

    # "DA SEMANA" — subtitle in track light
    f_s = font("title", int(118 * scale))
    center_text(draw, int(726 * scale), "DA SEMANA", f_s, cfg["primary_light"], W, shadow=True)

    # Divider line with endpoints
    lw  = int(380 * scale)
    lx  = (W - lw) // 2
    ly  = int(892 * scale)
    draw.line([(lx, ly), (lx + lw, ly)], fill=cfg["primary"],
              width=max(2, int(2 * scale)))
    dot_r = max(4, int(5 * scale))
    for ex in (lx, lx + lw):
        draw.ellipse([ex - dot_r, ly - dot_r, ex + dot_r, ly + dot_r],
                     fill=cfg["primary_light"])

    # Period
    if track.period_start and track.period_end:
        f_p = font("regular", int(32 * scale))
        center_text(draw, int(910 * scale),
                    f"{track.period_start}  ·  {track.period_end}",
                    f_p, (180, 180, 180), W)

    # Track name — colored pill badge
    f_t      = font("bold", int(52 * scale))
    bb       = draw.textbbox((0, 0), cfg["name"], font=f_t)
    tw, th   = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(36 * scale), int(13 * scale)
    pill_w   = tw + px_ * 2
    pill_h   = th + py_ * 2
    pill_x   = (W - pill_w) // 2
    pill_y   = int(975 * scale)
    # Badge fill: use primary_dark on bright bg (Campo Grande), primary on dark bg
    badge_fill = cfg["primary_dark"] if _lum(cfg["bg"]) > 0.25 else cfg["primary"]
    pill     = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle(
        [0, 0, pill_w - 1, pill_h - 1], radius=pill_h // 2,
        fill=(*badge_fill, 230),
    )
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              cfg["name"], font=f_t, fill=_text_on(badge_fill))

    return img


# ─── Ranking Slide ─────────────────────────────────────────────────────────────

def gen_ranking(track: Track, cat: Category, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    scale = min(W / 1080, H / 1350)

    # Background with two radial glows for depth
    img = Image.new("RGB", size, cfg["bg"])
    img = _add_radial_glow(img, int(W * 0.60), int(H * 0.26),
                           int(min(W, H) * 0.92), cfg["primary"], max_alpha=48)
    img = _add_radial_glow(img, int(W * 0.15), int(H * 0.78),
                           int(min(W, H) * 0.38), cfg["primary_dark"], max_alpha=32)

    # F1 livery diagonal band (subtle)
    img = _add_diagonal_band(img, cfg["primary"],
                             y_left=0.72, y_right=0.50, thickness=0.15, alpha=18)

    # Checkered flag — top-left, faded
    flag_sz = int(295 * scale)
    checker = _make_checker_faded(flag_sz, int(30 * scale))
    img.paste(checker, (-int(10 * scale), -int(10 * scale)), checker)

    draw = ImageDraw.Draw(img)

    # Top accent bar + bottom line
    bar_thick = max(8, int(10 * scale))
    draw.rectangle([0, 0, W, bar_thick], fill=cfg["primary_light"])
    draw.rectangle([0, H - max(3, int(3 * scale)), W, H], fill=cfg["primary"])

    # Small header row: track name left, "RANKING DA SEMANA" right
    f_head   = font("bold", int(24 * scale))
    hy       = int(22 * scale)
    bg_lum   = _lum(cfg["bg"])
    hdr_main = cfg["primary_light"] if bg_lum < 0.30 else cfg["primary_dark"]
    hdr_sec  = (120, 120, 120) if bg_lum < 0.30 else (60, 22, 0)
    draw.text((int(60 * scale), hy), cfg["name"], font=f_head, fill=hdr_main)
    rt = "RANKING DA SEMANA"
    bb = draw.textbbox((0, 0), rt, font=f_head)
    draw.text((W - (bb[2] - bb[0]) - int(60 * scale), hy),
              rt, font=f_head, fill=hdr_sec)

    # Hero title
    f_title = font("title", int(88 * scale))
    center_text(draw, int(68 * scale), "RANKING DA SEMANA",
                f_title, (255, 255, 255), W, shadow=True)

    # Category pill badge
    f_cat  = font("bold", int(27 * scale))
    c_lbl  = cat.label.upper()
    bb     = draw.textbbox((0, 0), c_lbl, font=f_cat)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px_, py_ = int(30 * scale), int(14 * scale)
    pill_w = tw + px_ * 2
    pill_h = th + py_ * 2
    pill_x = (W - pill_w) // 2
    pill_y = int(172 * scale)
    cat_fill = cfg["primary_dark"] if _lum(cfg["bg"]) > 0.25 else cfg["primary"]
    pill   = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle(
        [0, 0, pill_w - 1, pill_h - 1], radius=pill_h // 2,
        fill=(*cat_fill, 220),
    )
    img.paste(pill, (pill_x, pill_y), pill)
    draw = ImageDraw.Draw(img)
    draw.text((pill_x + px_ - bb[0], pill_y + py_ - bb[1]),
              c_lbl, font=f_cat, fill=_text_on(cat_fill))

    # Column labels
    f_lbl  = font("regular", int(19 * scale))
    row_m  = int(60 * scale)
    row_w  = W - row_m * 2
    slant  = int(int(79 * scale) * 0.16)
    lbl_y  = int(233 * scale)
    draw.text((row_m + slant + int(12 * scale), lbl_y),
              "COMPETIDOR", font=f_lbl, fill=(100, 100, 100))
    bb_t = draw.textbbox((0, 0), "TEMPO", font=f_lbl)
    draw.text((row_m + row_w - slant - (bb_t[2] - bb_t[0]) - int(14 * scale), lbl_y),
              "TEMPO", font=f_lbl, fill=(100, 100, 100))

    # Rows — 1st place 12% taller
    row_h   = int(79 * scale)
    row_h_1 = int(row_h * 1.12)
    row_g   = int(6 * scale)
    start_y = int(258 * scale)

    y_cursor = start_y
    for entry in cat.entries:
        rh = row_h_1 if entry.pos == 1 else row_h

        # Podium separator after 3rd place
        if entry.pos == 4:
            sep_y = y_cursor - row_g // 2
            draw.line([(row_m, sep_y), (row_m + row_w, sep_y)],
                      fill=(*cfg["primary"], 55), width=max(1, int(1 * scale)))

        if entry.pos == 1:
            img = _add_radial_glow(img, W // 2, y_cursor + rh // 2,
                                   int(rh * 3.2), cfg["primary_light"], max_alpha=16)
        _draw_row(img, draw, row_m, y_cursor, row_w, rh, entry, cfg, scale)
        draw = ImageDraw.Draw(img)
        y_cursor += rh + row_g

    # Logo centered below rows
    logo_y = y_cursor + (H - y_cursor) // 2
    _place_logo(img, logo_y, int(295 * scale), int(72 * scale))

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
