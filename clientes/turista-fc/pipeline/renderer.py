"""
Stage 3 — Renderer
Gera PNGs 1080×1920 de stories do Turista FC.
Entrada: lista de dicts {kicker, titulo, corpo, corpo2 (opcional)}
Saída:   lista de caminhos de arquivo em output/
"""
from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import TypedDict

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
FONTS_DIR = BASE_DIR / "fonts"
ASSETS_DIR = BASE_DIR.parent / "identidade-visual"
LOGO_PATH  = ASSETS_DIR / "logo" / "logo-branca-transparente.png"
OUTPUT_DIR = BASE_DIR / "output"

FONT_TITLE  = FONTS_DIR / "SpecialGothic.ttf"
FONT_BODY   = FONTS_DIR / "Montserrat-SemiBold.ttf"
FONT_KICKER = FONTS_DIR / "Montserrat.ttf"

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------
BLUE = (43,  37,  234)
OFF  = (249, 248, 248)
TEAL = (85,  214, 190)
RED  = (198, 41,  50)
DARK = (19,  19,  19)

W, H = 1080, 1920


class StoryData(TypedDict):
    kicker: str
    titulo: str          # até ~3 linhas no layout
    corpo:  str
    corpo2: str          # opcional — segunda caixa de texto


# ---------------------------------------------------------------------------
# Helpers de texto
# ---------------------------------------------------------------------------

def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _center_x(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    return (W - draw.textlength(text, font=font)) // 2


def _draw_centered(draw: ImageDraw.ImageDraw, y: int, text: str,
                   font: ImageFont.FreeTypeFont, fill: tuple) -> int:
    """Desenha texto centrado. Retorna y após o texto."""
    x = _center_x(draw, text, font)
    draw.text((x, y), text, font=font, fill=fill)
    bbox = font.getbbox(text)
    return y + (bbox[3] - bbox[1])


def _draw_centered_ls(draw: ImageDraw.ImageDraw, y: int, text: str,
                      font: ImageFont.FreeTypeFont, fill: tuple,
                      letter_spacing: int = 3) -> int:
    """Centraliza com letter-spacing manual (para kicker)."""
    total_w = sum(draw.textlength(ch, font=font) for ch in text) + letter_spacing * (len(text) - 1)
    x = (W - total_w) // 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + letter_spacing
    bbox = font.getbbox(text)
    return y + (bbox[3] - bbox[1])


def _wrap_title(draw: ImageDraw.ImageDraw, text: str,
                font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """
    Quebra o título em linhas respeitando max_width.
    Tenta primeiro quebra por palavras; força quebra de caractere se uma
    palavra única exceder o limite.
    """
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _wrap_body(draw: ImageDraw.ImageDraw, text: str,
               font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Quebra parágrafos de corpo por palavras."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Fundo degradê
# ---------------------------------------------------------------------------

def _make_background() -> Image.Image:
    base = np.array(Image.new("RGB", (W, H), BLUE), dtype=float)
    for y in range(H):
        f = max(0.0, (y - 1100) / (H - 1100)) * 0.30
        base[y] *= (1 - f)
    return Image.fromarray(base.astype("uint8"))


# ---------------------------------------------------------------------------
# Renderizador principal
# ---------------------------------------------------------------------------

def render_story(data: StoryData, index: int) -> Path:
    """Gera um PNG de story e retorna o caminho do arquivo."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    img = _make_background()
    draw = ImageDraw.Draw(img)

    # --- Fontes ---
    font_title  = _load_font(FONT_TITLE,  58)   # Special Gothic — maiores que 58 estouram em 3 palavras longas
    font_kicker = _load_font(FONT_KICKER, 32)
    font_body   = _load_font(FONT_BODY,   38)
    font_small  = _load_font(FONT_BODY,   28)

    MARGIN     = 80
    MAX_W_TEXT = W - 2 * MARGIN

    # --- Logo ---
    logo = Image.open(LOGO_PATH).convert("RGBA")
    lw = 280
    lh = int(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo, ((W - lw) // 2, 100), logo)

    y = 100 + lh + 60  # âncora após logo

    # --- Kicker ---
    kicker_text = data["kicker"].upper()
    kw = draw.textlength(kicker_text, font=font_kicker) + 3 * (len(kicker_text) - 1)
    bar_x0 = (W - kw) // 2 - 28
    draw.rectangle([(bar_x0, y + 4), (bar_x0 + 12, y + 34)], fill=TEAL)
    _draw_centered_ls(draw, y, kicker_text, font_kicker, OFF, letter_spacing=3)
    bbox_k = font_kicker.getbbox("A")
    y += (bbox_k[3] - bbox_k[1]) + 32

    # --- Título ---
    title_lines = _wrap_title(draw, data["titulo"].upper(), font_title, MAX_W_TEXT)
    # Colorir a última linha em TEAL para destaque visual
    for i, line in enumerate(title_lines):
        fill = TEAL if i == len(title_lines) - 1 else OFF
        x = _center_x(draw, line, font_title)
        draw.text((x, y), line, font=font_title, fill=fill)
        bbox_t = font_title.getbbox(line)
        y += (bbox_t[3] - bbox_t[1]) + 12
    y += 24  # espaço extra pós-título

    # --- Corpo principal ---
    body_lines = _wrap_body(draw, data["corpo"], font_body, MAX_W_TEXT)
    for line in body_lines:
        _draw_centered(draw, y, line, font_body, OFF)
        bbox_b = font_body.getbbox("A")
        y += (bbox_b[3] - bbox_b[1]) + 14
    y += 20

    # --- Divisor teal ---
    div_w = 100
    div_h = 4
    draw.rectangle([(W - div_w) // 2, y, (W + div_w) // 2, y + div_h], fill=TEAL)
    y += div_h + 30

    # --- Corpo 2 (opcional) ---
    corpo2 = data.get("corpo2", "").strip()
    if corpo2:
        body2_lines = _wrap_body(draw, corpo2, font_body, MAX_W_TEXT)
        for line in body2_lines:
            _draw_centered(draw, y, line, font_body, OFF)
            bbox_b2 = font_body.getbbox("A")
            y += (bbox_b2[3] - bbox_b2[1]) + 14
        y += 20

    # --- Rodapé institucional ---
    footer_lines = [
        "Viva os grandes eventos do esporte",
        "com quem cuida de tudo.",
    ]
    yf = H - 180
    for line in footer_lines:
        _draw_centered(draw, yf, line, font_small, OFF)
        bbox_s = font_small.getbbox("A")
        yf += (bbox_s[3] - bbox_s[1]) + 10

    # --- Salvar ---
    out_path = OUTPUT_DIR / f"story_{index:02d}.png"
    img.save(str(out_path))
    return out_path


def render_all(stories: list[StoryData]) -> list[Path]:
    paths = []
    for i, story in enumerate(stories, start=1):
        path = render_story(story, i)
        print(f"  [renderer] {i}/5 -> {path.name}")
        paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# Teste local (python renderer.py)
# ---------------------------------------------------------------------------

SAMPLE_STORIES: list[StoryData] = [
    {
        "kicker": "Champions League",
        "titulo": "Vinicius brilha na final",
        "corpo": "O atacante brasileiro marcou dois gols e foi eleito o melhor jogador da final da Champions League em Munique.",
        "corpo2": "Real Madrid conquista o 16o titulo europeu. Uma noite historica para o futebol brasileiro.",
    },
    {
        "kicker": "Formula 1",
        "titulo": "Verstappen domina em Monaco",
        "corpo": "Max Verstappen venceu o Grande Premio de Monaco de ponta a ponta, ampliando sua liderança no campeonato.",
        "corpo2": "",
    },
    {
        "kicker": "Copa do Mundo 2026",
        "titulo": "Brasil conhece adversarios",
        "corpo": "A selecao brasileira foi sorteada no Grupo D com Argentina, Alemanha e Marrocos na fase de grupos do Mundial.",
        "corpo2": "Jogos no Mexico e nos Estados Unidos. Ingressos com alta demanda global.",
    },
    {
        "kicker": "Roland Garros",
        "titulo": "Sinner avanca as semifinais",
        "corpo": "O numero 1 do mundo superou o frances Gasquet em sets diretos e garantiu vaga na semifinal de Roland Garros.",
        "corpo2": "",
    },
    {
        "kicker": "MotoGP",
        "titulo": "Marquez conquista Mugello",
        "corpo": "Marc Marquez triunfou no Grande Premio da Italia em Mugello, sua pista favorita, em corrida disputadissima.",
        "corpo2": "Bagnaia terminou em segundo e permanece lider do campeonato por apenas 4 pontos.",
    },
]

if __name__ == "__main__":
    print("Renderizando 5 stories de teste...")
    paths = render_all(SAMPLE_STORIES)
    print(f"\nGerados: {[p.name for p in paths]}")
    print(f"Pasta: {OUTPUT_DIR}")
