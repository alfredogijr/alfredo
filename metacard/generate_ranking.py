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
from typing import List, Optional
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
        "primary":       ( 98,  46, 188),
        "primary_dark":  ( 55,  25, 112),
        "primary_light": (148,  90, 230),
        "bg":            ( 11,   7,  28),
        "row_bg":        ( 82,  38, 162),
        "num_bg":        ( 20,  11,  46),
    },
    "norte": {
        "name":          "NORTE",
        "primary":       ( 25, 115,  38),
        "primary_dark":  ( 12,  65,  20),
        "primary_light": ( 50, 170,  65),
        "bg":            (  5,  14,   7),
        "row_bg":        ( 20,  92,  30),
        "num_bg":        (  8,  22,  11),
    },
    "campo_grande": {
        "name":          "CAMPO GRANDE",
        "primary":       (210,  78,  12),
        "primary_dark":  (120,  40,   5),
        "primary_light": (245, 130,  50),
        "bg":            ( 18,   8,   2),
        "row_bg":        (185,  68,  10),
        "num_bg":        ( 32,  14,   4),
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

# Top-3 medal palette
_MEDAL = {
    1: {"bar_l": (215, 175, 28),  "bar_r": (155, 118, 12),  "num": (120, 90, 8)},
    2: {"bar_l": (178, 183, 195), "bar_r": (128, 133, 145), "num": (95, 100, 112)},
    3: {"bar_l": (188, 112, 42),  "bar_r": (145, 78, 25),   "num": (108, 55, 16)},
}


def _lerp_color(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def center_text(draw: ImageDraw.Draw, y: int, text: str,
                fnt: ImageFont.FreeTypeFont, color: tuple, canvas_w: int,
                shadow: bool = False) -> int:
    bb  = draw.textbbox((0, 0), text, font=fnt)
    tw  = bb[2] - bb[0]
    x   = (canvas_w - tw) // 2 - bb[0]
    if shadow:
        for ox, oy in [(3, 3), (2, 3), (3, 2)]:
            draw.text((x + ox, y + oy), text, font=fnt, fill=(0, 0, 0, 120))
    draw.text((x, y), text, font=fnt, fill=color)
    return bb[3] - bb[1]


def _gradient_bar(w: int, h: int, col_l: tuple, col_r: tuple) -> Image.Image:
    """1-row gradient stretched to full height — fast approach."""
    bar = Image.new("RGB", (w, 1))
    px  = bar.load()
    for x in range(w):
        px[x, 0] = _lerp_color(col_l, col_r, x / max(w - 1, 1))
    return bar.resize((w, h), Image.NEAREST)


def _add_radial_glow(img: Image.Image, cx: int, cy: int,
                     radius: int, color: tuple, max_alpha: int = 60) -> Image.Image:
    """Soft radial glow using concentric ellipses + gaussian blur."""
    W, H  = img.size
    glow  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    steps = 20
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(max_alpha * (i / steps) ** 1.8)
        gdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 6))
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def _make_checker_faded(size: int, cell: int) -> Image.Image:
    """Checkered pattern that fades diagonally from the top-left corner."""
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    n    = size // cell + 2
    diag = (size ** 2 * 2) ** 0.5
    for r in range(n):
        for c in range(n):
            if (r + c) % 2 == 0:
                dist  = ((r * cell) ** 2 + (c * cell) ** 2) ** 0.5
                alpha = int(140 * max(0.0, 1.0 - (dist / diag) * 1.6) ** 1.4)
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


def _place_logo(img: Image.Image, y_center: int, max_w: int, max_h: int) -> None:
    logo   = Image.open(LOGO).convert("RGBA")
    sc     = min(max_w / logo.width, max_h / logo.height)
    lw, lh = int(logo.width * sc), int(logo.height * sc)
    logo   = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo, ((img.width - lw) // 2, y_center - lh // 2), logo)


def _draw_row(img: Image.Image, draw: ImageDraw.Draw,
              x: int, y: int, w: int, h: int,
              entry: Entry, cfg: dict) -> None:
    gap   = 4
    bar_h = h - gap
    pos_w = int(h * 0.92)
    r_corner = max(5, int(bar_h * 0.13))

    # Choose colors (medal or track)
    if entry.pos in _MEDAL:
        mc    = _MEDAL[entry.pos]
        bar_l, bar_r = mc["bar_l"], mc["bar_r"]
        num_c = mc["num"]
    else:
        bar_l = cfg["row_bg"]
        bar_r = _lerp_color(cfg["row_bg"], cfg["bg"], 0.38)
        num_c = cfg["num_bg"]

    # Gradient bar (full width, will be masked by rounded rect below)
    grad  = _gradient_bar(w, bar_h, bar_l, bar_r)
    img.paste(grad, (x, y))

    # Position box overlay
    num_img = Image.new("RGBA", (pos_w, bar_h), (*num_c, 245))
    img.paste(num_img, (x, y), num_img)

    # Left accent stripe (3 px, bright primary_light)
    draw.rectangle([x, y, x + 4, y + bar_h - 1], fill=cfg["primary_light"])

    # Re-acquire draw (img was modified by paste)
    draw = ImageDraw.Draw(img)

    # Position number
    f_pos  = font("bold", int(h * 0.46))
    bb     = draw.textbbox((0, 0), str(entry.pos), font=f_pos)
    pw, ph = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(
        (x + 4 + (pos_w - 4 - pw) // 2 - bb[0],
         y + (bar_h - ph) // 2 - bb[1]),
        str(entry.pos), font=f_pos, fill=(255, 255, 255)
    )

    # Name (truncate if too wide)
    f_name    = font("bold", int(h * 0.295))
    name_x    = x + pos_w + 16
    max_name_w = w - pos_w - 20 - 160   # leave room for time
    name_str   = entry.name
    while True:
        bb = draw.textbbox((0, 0), name_str, font=f_name)
        if (bb[2] - bb[0]) <= max_name_w or len(name_str) < 4:
            break
        name_str = name_str[:-1]
    if name_str != entry.name:
        name_str = name_str.rstrip() + "…"
    bb = draw.textbbox((0, 0), name_str, font=f_name)
    draw.text(
        (name_x, y + (bar_h - (bb[3] - bb[1])) // 2 - bb[1]),
        name_str, font=f_name, fill=(255, 255, 255)
    )

    # Time (right-aligned, mono-spaced feel)
    f_time = font("bold", int(h * 0.33))
    bb     = draw.textbbox((0, 0), entry.time, font=f_time)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(
        (x + w - tw - 18, y + (bar_h - th) // 2 - bb[1]),
        entry.time, font=f_time, fill=(255, 255, 255)
    )


# ─── Cover Slide ───────────────────────────────────────────────────────────────

def gen_cover(track: Track, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    scale = min(W / 1080, H / 1350)

    # Background: vertical gradient + radial glow
    img = _vertical_gradient(size, cfg["primary_dark"], cfg["bg"])
    img = _add_radial_glow(img, W // 2, int(H * 0.28),
                           int(min(W, H) * 0.72), cfg["primary"], max_alpha=50)

    # Faint watermark "RANKING" in background
    wm_size = int(210 * scale)
    f_wm    = font("title", wm_size)
    wm_img  = Image.new("RGBA", size, (0, 0, 0, 0))
    wm_draw = ImageDraw.Draw(wm_img)
    bb      = wm_draw.textbbox((0, 0), "RANKING", font=f_wm)
    wm_x    = (W - (bb[2] - bb[0])) // 2 - bb[0]
    wm_draw.text((wm_x, int(H * 0.38)), "RANKING", font=f_wm,
                 fill=(*cfg["primary"], 22))
    img = Image.alpha_composite(img.convert("RGBA"), wm_img).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Logo
    _place_logo(img, int(295 * scale), int(480 * scale), int(185 * scale))
    draw = ImageDraw.Draw(img)

    # "RANKING"
    f_r = font("title", int(168 * scale))
    center_text(draw, int(555 * scale), "RANKING", f_r, (255, 255, 255), W, shadow=True)

    # "DA SEMANA"
    f_s = font("title", int(115 * scale))
    center_text(draw, int(728 * scale), "DA SEMANA", f_s, cfg["primary_light"], W, shadow=True)

    # Divider line (with dots at ends)
    lw = int(360 * scale)
    lx = (W - lw) // 2
    ly = int(880 * scale)
    draw.line([(lx, ly), (lx + lw, ly)], fill=cfg["primary"], width=2)
    dot_r = 4
    draw.ellipse([lx - dot_r, ly - dot_r, lx + dot_r, ly + dot_r],
                 fill=cfg["primary_light"])
    draw.ellipse([lx + lw - dot_r, ly - dot_r, lx + lw + dot_r, ly + dot_r],
                 fill=cfg["primary_light"])

    # Period
    if track.period_start and track.period_end:
        f_p = font("semibold", int(34 * scale))
        center_text(draw, int(898 * scale),
                    f"{track.period_start}  ·  {track.period_end}",
                    f_p, (200, 200, 200), W)

    # Track name
    f_t = font("bold", int(58 * scale))
    center_text(draw, int(958 * scale), cfg["name"], f_t, (255, 255, 255), W, shadow=True)

    return img


# ─── Ranking Slide ─────────────────────────────────────────────────────────────

def gen_ranking(track: Track, cat: Category, cfg: dict, size: tuple) -> Image.Image:
    W, H  = size
    scale = min(W / 1080, H / 1350)

    # Background
    img = Image.new("RGB", size, cfg["bg"])
    img = _add_radial_glow(img, int(W * 0.55), int(H * 0.32),
                           int(min(W, H) * 0.85), cfg["primary"], max_alpha=42)

    # Checkered flag (top-left, faded diagonally)
    flag_sz = int(310 * scale)
    checker = _make_checker_faded(flag_sz, int(31 * scale))
    img.paste(checker, (-int(12 * scale), -int(12 * scale)), checker)

    draw = ImageDraw.Draw(img)

    # Thin colored top border
    draw.rectangle([0, 0, W, int(6 * scale)], fill=cfg["primary_light"])

    # Title "RANKING DA SEMANA"
    f_title = font("title", int(84 * scale))
    center_text(draw, int(195 * scale), "RANKING DA SEMANA",
                f_title, (255, 255, 255), W, shadow=True)

    # Category label with underline accent
    f_cat  = font("semibold", int(31 * scale))
    cat_y  = int(296 * scale)
    cat_h  = center_text(draw, cat_y, f"CATEGORIA:  {cat.label}",
                         f_cat, cfg["primary_light"], W)
    # Underline
    cat_text = f"CATEGORIA:  {cat.label}"
    bb = draw.textbbox((0, 0), cat_text, font=f_cat)
    uw = bb[2] - bb[0]
    ux = (W - uw) // 2
    uy = cat_y + cat_h + int(6 * scale)
    draw.line([(ux, uy), (ux + uw, uy)], fill=cfg["primary"], width=2)

    # Rows
    row_m  = int(62 * scale)
    row_w  = W - row_m * 2
    row_h  = int(80 * scale)
    row_g  = int(6  * scale)
    start_y = int(362 * scale)

    for entry in cat.entries:
        ry = start_y + (entry.pos - 1) * (row_h + row_g)
        _draw_row(img, draw, row_m, ry, row_w, row_h, entry, cfg)
        draw = ImageDraw.Draw(img)   # refresh after paste ops

    # Logo
    rows_end = start_y + 10 * (row_h + row_g)
    logo_y   = rows_end + (H - rows_end) // 2
    _place_logo(img, logo_y, int(330 * scale), int(82 * scale))

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
