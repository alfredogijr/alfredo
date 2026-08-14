#!/usr/bin/env python3
"""
Gera os arquivos de legenda (.ass) do institucional de 35s do Meta Kart.

Especificação de arte pedida no briefing:
  - texto branco em negrito
  - sombra ou fundo semitransparente
  - sempre centralizado na parte inferior do quadro

Uso:
    python3 gerar-legendas.py                 # gera 16x9 e 9x16, estilo "caixa"
    python3 gerar-legendas.py --estilo sombra # variante com sombra em vez de caixa
    python3 gerar-legendas.py --fonte "Montserrat"   # troca a fonte de marca
"""

import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Blocos de texto — tempos exatos conforme o briefing.
# O \N marca a quebra de linha e existe só para equilibrar o bloco de texto.
# ---------------------------------------------------------------------------
BLOCOS = [
    (0.0,  3.0,  r"Três pistas. Uma só experiência."),
    (3.0,  8.0,  r"No NorteShopping, você encontra\Na pista mais longa do Rio de Janeiro."),
    (8.0,  13.0, r"Na Barra, o único túnel de LED\Ndo Rio de Janeiro te leva pra outro nível."),
    (13.0, 18.0, r"Em Campo Grande, um traçado técnico que\Nexige leitura e precisão em cada curva."),
    (18.0, 22.0, r"Três estruturas.\NUma só referência em kart indoor."),
    (22.0, 27.0, r"Espaço pensado pra receber você e seus\Nconvidados antes, durante e depois da corrida."),
    (27.0, 31.0, r"Cada detalhe pensado pra transformar\Nseu evento em uma experiência completa."),
    (31.0, 35.0, r"Reserve sua próxima corrida pelo WhatsApp."),
]

# Fade de entrada/saída do texto, em milissegundos. Curto o bastante para
# acompanhar o ritmo acelerado sem piscar em cima do corte.
FADE_MS = 150

FORMATOS = {
    "16x9": dict(w=1920, h=1080, fontsize=52, margin_v=84,  margin_h=260),
    "9x16": dict(w=1080, h=1920, fontsize=58, margin_v=260, margin_h=90),
}


def ts(segundos: float) -> str:
    """Converte segundos para o timecode do ASS (h:mm:ss.cc)."""
    centesimos = int(round(segundos * 100))
    h, resto = divmod(centesimos, 360000)
    m, resto = divmod(resto, 6000)
    s, cs = divmod(resto, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def montar_estilo(fmt: dict, fonte: str, estilo: str) -> str:
    """
    Monta a linha Style do ASS.

    ASS usa alfa invertido: 00 = opaco, FF = transparente.
    BorderStyle 3 = caixa opaca (usamos BackColour com alfa para deixá-la
    semitransparente). BorderStyle 1 = contorno + sombra projetada.
    """
    if estilo == "caixa":
        border_style, outline, shadow = 3, 18, 0
        back_colour = "&H59000000"   # preto a ~65% de opacidade
    else:  # sombra
        border_style, outline, shadow = 1, 0, 5
        back_colour = "&H96000000"   # sombra preta suave

    return (
        f"Style: Legenda,{fonte},{fmt['fontsize']},"
        f"&H00FFFFFF,&H00FFFFFF,&H00000000,{back_colour},"
        f"-1,0,0,0,100,100,0,0,"                      # -1 = negrito ligado
        f"{border_style},{outline},{shadow},"
        f"2,"                                          # alinhamento 2 = inferior centralizado
        f"{fmt['margin_h']},{fmt['margin_h']},{fmt['margin_v']},1"
    )


def gerar(formato: str, fonte: str, estilo: str, destino: Path) -> Path:
    fmt = FORMATOS[formato]

    cabecalho = f"""[Script Info]
Title: Meta Kart - institucional 35s ({formato})
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {fmt['w']}
PlayResY: {fmt['h']}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{montar_estilo(fmt, fonte, estilo)}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    linhas = [
        f"Dialogue: 0,{ts(ini)},{ts(fim)},Legenda,,0,0,0,,"
        f"{{\\fad({FADE_MS},{FADE_MS})}}{texto}"
        for ini, fim, texto in BLOCOS
    ]

    saida = destino / f"legendas-{formato}.ass"
    saida.write_text(cabecalho + "\n".join(linhas) + "\n", encoding="utf-8")
    return saida


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fonte", default="DejaVu Sans",
                   help="Família da fonte. Troque pela fonte de marca do Meta Kart.")
    p.add_argument("--estilo", choices=["caixa", "sombra"], default="caixa",
                   help="caixa = fundo semitransparente; sombra = sombra projetada.")
    p.add_argument("--destino", default=".", help="Diretório de saída.")
    args = p.parse_args()

    destino = Path(args.destino)
    destino.mkdir(parents=True, exist_ok=True)

    for formato in FORMATOS:
        caminho = gerar(formato, args.fonte, args.estilo, destino)
        print(f"gerado: {caminho}")


if __name__ == "__main__":
    main()
