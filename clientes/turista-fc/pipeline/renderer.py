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

# ---------------------------------------------------------------------------
# Âncoras absolutas de diagramação (zonas fixas para consistência entre stories)
# ---------------------------------------------------------------------------
LOGO_MARGIN_TOP = 120   # zona segura superior
TITLE_TOP_Y     = 560   # topo do título sempre fixo, independente do kicker
BODY_TOP_Y      = 1050  # início do corpo sempre fixo
FOOTER_TOP_Y    = 1760  # topo do rodapé sempre fixo
BODY_LINE_H     = 56    # espaçamento de linha do corpo
GAP_AFTER_DIV   = 48    # gap após divisor antes do corpo2


def _title_font_size(title_lines: list[str]) -> int:
    """Font size adaptativo conforme comprimento da linha mais longa."""
    longest = max((len(line) for line in title_lines), default=0)
    if longest > 16:
        return 40
    if longest > 12:
        return 48
    return 58


def render_story(data: StoryData, index: int) -> Path:
    """Gera um PNG de story e retorna o caminho do arquivo."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    img = _make_background()
    draw = ImageDraw.Draw(img)

    # --- Fontes ---
    font_kicker = _load_font(FONT_KICKER, 32)
    font_body   = _load_font(FONT_BODY,   38)
    font_small  = _load_font(FONT_BODY,   28)
    font_edition = _load_font(FONT_BODY,  22)

    MARGIN     = 80
    MAX_W_TEXT = W - 2 * MARGIN

    # --- Logo (zona segura: 120px de margin-top) ---
    logo = Image.open(LOGO_PATH).convert("RGBA")
    lw = 280
    lh = int(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo, ((W - lw) // 2, LOGO_MARGIN_TOP), logo)

    # --- Kicker (centrado verticalmente na zona entre logo e título) ---
    kicker_text = data["kicker"].upper()
    bbox_k = font_kicker.getbbox("Ay")
    kicker_h = bbox_k[3] - bbox_k[1]
    # posiciona o kicker com respiro: a meio caminho da zona livre
    logo_bottom = LOGO_MARGIN_TOP + lh
    y_kicker = logo_bottom + (TITLE_TOP_Y - logo_bottom - kicker_h) // 2

    # linha decorativa acima do kicker (2px alt, 60px larg, 20px acima)
    deco_w, deco_h = 60, 2
    deco_y = y_kicker - 20 - deco_h
    draw.rectangle(
        [(W - deco_w) // 2, deco_y, (W + deco_w) // 2, deco_y + deco_h],
        fill=TEAL,
    )

    # barra teal lateral com 16px de gap entre barra e texto
    kw = draw.textlength(kicker_text, font=font_kicker) + 3 * (len(kicker_text) - 1)
    bar_w = 12
    bar_gap = 16
    bar_x1 = (W - kw) // 2 - bar_gap
    bar_x0 = bar_x1 - bar_w
    draw.rectangle([(bar_x0, y_kicker + 4), (bar_x1, y_kicker + 34)], fill=TEAL)
    _draw_centered_ls(draw, y_kicker, kicker_text, font_kicker, OFF, letter_spacing=3)

    # --- Título (topo fixo em TITLE_TOP_Y) ---
    # Mede com a maior fonte; reduz adaptativamente e re-quebra.
    font_title = _load_font(FONT_TITLE, 58)
    title_lines = _wrap_title(draw, data["titulo"].upper(), font_title, MAX_W_TEXT)
    size = _title_font_size(title_lines)
    if size != 58:
        font_title = _load_font(FONT_TITLE, size)
        title_lines = _wrap_title(draw, data["titulo"].upper(), font_title, MAX_W_TEXT)

    # Regra de cor: colorir a última linha em TEAL apenas se houver 2+ linhas
    # E a última linha tiver <= 2 palavras (linha de impacto curta).
    n = len(title_lines)
    last_words = len(title_lines[-1].split()) if title_lines else 0
    highlight_last = n >= 2 and last_words <= 2

    y = TITLE_TOP_Y
    for i, line in enumerate(title_lines):
        is_last = i == n - 1
        fill = TEAL if (highlight_last and is_last) else OFF
        x = _center_x(draw, line, font_title)
        draw.text((x, y), line, font=font_title, fill=fill)
        bbox_t = font_title.getbbox(line)
        y += (bbox_t[3] - bbox_t[1]) + 12

    # --- Corpo principal (início fixo em BODY_TOP_Y) ---
    y = BODY_TOP_Y
    body_lines = _wrap_body(draw, data["corpo"], font_body, MAX_W_TEXT)
    for line in body_lines:
        _draw_centered(draw, y, line, font_body, OFF)
        y += BODY_LINE_H
    y += 20

    # --- Divisor teal (mais presente: 6px alt, 140px larg) ---
    div_w = 140
    div_h = 6
    draw.rectangle([(W - div_w) // 2, y, (W + div_w) // 2, y + div_h], fill=TEAL)
    y += div_h + GAP_AFTER_DIV

    # --- Corpo 2 (opcional) ---
    corpo2 = data.get("corpo2", "").strip()
    if corpo2:
        body2_lines = _wrap_body(draw, corpo2, font_body, MAX_W_TEXT)
        for line in body2_lines:
            _draw_centered(draw, y, line, font_body, OFF)
            y += BODY_LINE_H

    # --- Rodapé institucional (topo fixo em FOOTER_TOP_Y) ---
    footer_lines = [
        "Viva os grandes eventos do esporte",
        "com quem cuida de tudo.",
    ]
    yf = FOOTER_TOP_Y
    for line in footer_lines:
        _draw_centered(draw, yf, line, font_small, OFF)
        bbox_s = font_small.getbbox("A")
        yf += (bbox_s[3] - bbox_s[1]) + 10

    # --- Número de edição (canto inferior direito) ---
    edition = f"{index:02d}/{5:02d}"
    draw.text((970, 1840), edition, font=font_edition, fill=TEAL)

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
