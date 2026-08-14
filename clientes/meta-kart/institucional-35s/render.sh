#!/usr/bin/env bash
#
# Monta o institucional de 35s do Meta Kart a partir de cortes.csv.
#
#   ./render.sh                 # 16x9 (1920x1080), material real em fontes/
#   ./render.sh 9x16            # vertical (1080x1920)
#   ./render.sh 16x9 --prova    # prova de tempo: placas em vez do material bruto
#
# Requisitos: ffmpeg com libass (o filtro "subtitles").
# Se nao houver ffmpeg no sistema:  pip install imageio-ffmpeg
# e aponte FFMPEG para o binario instalado.

set -euo pipefail
cd "$(dirname "$0")"

FORMATO="${1:-16x9}"
MODO="${2:-real}"

case "$FORMATO" in
  16x9) W=1920; H=1080 ;;
  9x16) W=1080; H=1920 ;;
  *) echo "formato invalido: $FORMATO (use 16x9 ou 9x16)" >&2; exit 1 ;;
esac

FPS=30
LEGENDAS="legendas-${FORMATO}.ass"
TRILHA="fontes/trilha.m4a"
if [[ "$MODO" == "--prova" ]]; then
  SAIDA="PROVA-tempo-${FORMATO}.mp4"
else
  SAIDA="meta-kart-institucional-35s-${FORMATO}.mp4"
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Descobre o ffmpeg: o do sistema ou o empacotado pelo imageio-ffmpeg.
FFMPEG="${FFMPEG:-$(command -v ffmpeg || true)}"
if [[ -z "$FFMPEG" ]]; then
  FFMPEG="$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || true)"
fi
[[ -n "$FFMPEG" ]] || { echo "ffmpeg nao encontrado. Rode: pip install imageio-ffmpeg" >&2; exit 1; }

[[ -f "$LEGENDAS" ]] || { echo "faltando $LEGENDAS. Rode: python3 gerar-legendas.py" >&2; exit 1; }

# Enquadra qualquer proporcao de origem no formato de saida sem distorcer:
# cobre o quadro e corta o excedente.
ENQUADRA="scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H}"
# Leve zoom in ao longo do corte (o "leve zoom" pedido no briefing).
ZOOM="zoompan=z='min(zoom+0.0006,1.08)':d=1:s=${W}x${H}:fps=${FPS}"

echo ">> formato ${FORMATO} (${W}x${H}), modo ${MODO}"

n=0
: > "$TMP/lista.txt"

# Le cortes.csv ignorando comentarios e cabecalho.
while IFS=, read -r bloco arquivo entrada dur zoom descricao; do
  [[ "$bloco" =~ ^#|^bloco$|^$ ]] && continue
  n=$((n + 1))
  peca="$TMP/$(printf '%03d' "$n").mp4"

  if [[ "$MODO" == "--prova" ]]; then
    # Placa cinza numerada, so para validar tempo e legibilidade do texto.
    tom=$(( 24 + (bloco * 9) ))
    "$FFMPEG" -hide_banner -nostdin -loglevel error -y \
      -f lavfi -i "color=c=0x$(printf '%02x%02x%02x' $tom $tom $((tom + 6))):s=${W}x${H}:r=${FPS}:d=${dur}" \
      -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$peca"
  else
    origem="fontes/$arquivo"
    [[ -f "$origem" ]] || { echo "faltando $origem (ver mapa-de-material.md)" >&2; exit 1; }
    filtro="$ENQUADRA"
    [[ "$zoom" == "1" ]] && filtro="$filtro,$ZOOM"
    # -ss antes do -i faz busca rapida; -t depois limita a duracao do corte.
    "$FFMPEG" -hide_banner -nostdin -loglevel error -y \
      -ss "$entrada" -i "$origem" -t "$dur" \
      -vf "${filtro},fps=${FPS},setsar=1" -an \
      -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$peca"
  fi

  printf "file '%s'\n" "$peca" >> "$TMP/lista.txt"
  printf "  corte %02d | bloco %s | %5.1fs | %s\n" "$n" "$bloco" "$dur" "$descricao"
done < cortes.csv

echo ">> juntando $n cortes"
"$FFMPEG" -hide_banner -nostdin -loglevel error -y \
  -f concat -safe 0 -i "$TMP/lista.txt" -c copy "$TMP/bruto.mp4"

# Trilha: entra se existir. Sem trilha, o video sai mudo (o briefing pede
# instrumental energetica sem vocal - ver "Trilha" no roteiro-decupagem.md).
if [[ -f "$TRILHA" ]]; then
  echo ">> aplicando trilha: $TRILHA"
  AUDIO_IN=(-i "$TRILHA")
  AUDIO_MAP=(-map 1:a -c:a aac -b:a 192k -af "afade=t=out:st=34:d=1" -shortest)
else
  echo ">> sem trilha em $TRILHA - saida ficara muda"
  AUDIO_IN=()
  AUDIO_MAP=(-an)
fi

# Passe final: queima as legendas e aplica o fade out do ultimo bloco.
echo ">> queimando legendas e finalizando"
"$FFMPEG" -hide_banner -nostdin -loglevel error -y \
  -i "$TMP/bruto.mp4" "${AUDIO_IN[@]}" \
  -vf "subtitles=${LEGENDAS}:fontsdir=/usr/share/fonts,fade=t=out:st=34.4:d=0.6" \
  -map 0:v "${AUDIO_MAP[@]}" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart \
  -r "$FPS" "$SAIDA"

echo ">> pronto: $SAIDA"
"$FFMPEG" -hide_banner -i "$SAIDA" 2>&1 | grep -E "Duration|Stream" || true
