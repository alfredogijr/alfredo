#!/usr/bin/env bash
# Monta um video de fotos com transicao e texto queimado.
# Uso: ./gerar-video.sh -p <pasta-fotos> -t <arquivo-textos> [opcoes]
set -euo pipefail

PASTA=""
TEXTOS=""
SAIDA="video"
TOTAL=30
TRANS=0.5
FORMATO="ambos"           # reels | feed | ambos
FONTE="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MUSICA=""
FPS=30

uso() {
  cat <<'USO'
Uso: gerar-video.sh -p <pasta-fotos> -t <arquivo-textos> [opcoes]

  -p  pasta com as fotos (jpg/jpeg/png), usadas em ordem alfabetica
  -t  arquivo de textos: uma cena por linha, use | para quebrar linha
  -o  nome base do arquivo de saida            (padrao: video)
  -d  duracao total em segundos                (padrao: 30)
  -x  duracao da transicao em segundos         (padrao: 0.5)
  -f  formato: reels (9:16), feed (4:5), ambos (padrao: ambos)
  -F  caminho de um .ttf para o texto          (padrao: DejaVu Sans Bold)
  -m  trilha sonora .mp3/.m4a (opcional, cortada e com fade)

Exemplo:
  ./gerar-video.sh -p ~/Downloads/13a-etapa -t textos-13a-etapa.txt -o meta-kart-13a -m trilha.mp3
USO
}

while getopts "p:t:o:d:x:f:F:m:h" opt; do
  case "$opt" in
    p) PASTA="$OPTARG" ;;
    t) TEXTOS="$OPTARG" ;;
    o) SAIDA="$OPTARG" ;;
    d) TOTAL="$OPTARG" ;;
    x) TRANS="$OPTARG" ;;
    f) FORMATO="$OPTARG" ;;
    F) FONTE="$OPTARG" ;;
    m) MUSICA="$OPTARG" ;;
    h) uso; exit 0 ;;
    *) uso; exit 64 ;;
  esac
done

[ -d "${PASTA:-}" ] || { echo "erro: pasta de fotos invalida"; uso; exit 64; }
[ -f "${TEXTOS:-}" ] || { echo "erro: arquivo de textos invalido"; uso; exit 64; }
[ -f "$FONTE" ] || { echo "erro: fonte nao encontrada em $FONTE"; exit 64; }
command -v ffmpeg >/dev/null || { echo "erro: ffmpeg nao instalado"; exit 69; }

mapfile -t FOTOS < <(find "$PASTA" -maxdepth 1 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | sort)
mapfile -t CENAS < <(grep -v '^[[:space:]]*$' "$TEXTOS")

N_FOTOS=${#FOTOS[@]}
N_CENAS=${#CENAS[@]}
[ "$N_FOTOS" -ge 2 ] || { echo "erro: precisa de pelo menos 2 fotos"; exit 65; }

# uma cena por foto; sobra de texto e ignorada, falta de texto vira cena limpa
N=$N_FOTOS
[ "$N_CENAS" -lt "$N" ] && N=$N_CENAS
[ "$N" -ge 2 ] || { echo "erro: precisa de pelo menos 2 cenas com texto"; exit 65; }

# duracao de cada clipe, ja compensando as transicoes que se sobrepoem
DUR=$(awk -v t="$TOTAL" -v n="$N" -v x="$TRANS" 'BEGIN{printf "%.4f", (t + (n-1)*x)/n}')
MIN_DUR=$(awk -v x="$TRANS" 'BEGIN{printf "%.4f", x+0.4}')
awk -v d="$DUR" -v m="$MIN_DUR" 'BEGIN{exit !(d<m)}' && {
  echo "erro: $N cenas em ${TOTAL}s deixa cada foto com menos de ${MIN_DUR}s. Use menos fotos ou aumente -d"; exit 65; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

render() {
  local W=$1 H=$2 SUFIXO=$3
  local TAM_TEXTO=$(( W * 6 / 100 ))     # ~65px em 1080 de largura
  local MARGEM=$(( H * 13 / 100 ))
  local FRAMES=$(awk -v d="$DUR" -v f="$FPS" 'BEGIN{printf "%d", d*f}')

  echo ">> ${SUFIXO}: ${N} cenas de ${DUR}s em ${W}x${H}"

  for i in $(seq 0 $((N-1))); do
    printf '%s\n' "${CENAS[$i]//|/$'\n'}" > "$TMP/txt$i.txt"
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H}"
    FC="${FC},scale=$((W*2)):$((H*2)),setsar=1"
    FC="${FC},zoompan=z='min(zoom+0.0007,1.12)':d=${FRAMES}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=${W}x${H}:fps=${FPS}"
    FC="${FC},drawtext=fontfile='${FONTE}':textfile='${TMP}/txt${i}.txt':fontcolor=white:fontsize=${TAM_TEXTO}:line_spacing=$((TAM_TEXTO/4)):x=(w-text_w)/2:y=h-${MARGEM}-text_h:box=1:boxcolor=black@0.42:boxborderw=$((TAM_TEXTO/2)):shadowcolor=black@0.55:shadowx=2:shadowy=3"
    FC="${FC},format=yuv420p"
    ffmpeg -nostdin -loglevel error -y -loop 1 -t "$DUR" -i "${FOTOS[$i]}" \
      -filter_complex "$FC" -r "$FPS" -c:v libx264 -preset veryfast -crf 20 -an "$TMP/clip$i$SUFIXO.mp4"
  done

  # encadeia os clipes com xfade
  local INPUTS=() FILTRO="" ULTIMO="0:v" OFFSET
  for i in $(seq 0 $((N-1))); do INPUTS+=(-i "$TMP/clip$i$SUFIXO.mp4"); done
  for i in $(seq 1 $((N-1))); do
    OFFSET=$(awk -v d="$DUR" -v x="$TRANS" -v i="$i" 'BEGIN{printf "%.4f", i*(d-x)}')
    FILTRO+="[${ULTIMO}][${i}:v]xfade=transition=fade:duration=${TRANS}:offset=${OFFSET}[v${i}];"
    ULTIMO="v${i}"
  done
  FILTRO+="[${ULTIMO}]format=yuv420p[vout]"

  if [ -n "$MUSICA" ] && [ -f "$MUSICA" ]; then
    ffmpeg -nostdin -loglevel error -y "${INPUTS[@]}" -i "$MUSICA" \
      -filter_complex "${FILTRO};[${N}:a]atrim=0:${TOTAL},afade=t=in:st=0:d=1,afade=t=out:st=$(awk -v t="$TOTAL" 'BEGIN{print t-2}'):d=2[aout]" \
      -map "[vout]" -map "[aout]" -c:v libx264 -preset medium -crf 20 \
      -c:a aac -b:a 192k -shortest -movflags +faststart "${SAIDA}-${SUFIXO}.mp4"
  else
    ffmpeg -nostdin -loglevel error -y "${INPUTS[@]}" -filter_complex "$FILTRO" \
      -map "[vout]" -c:v libx264 -preset medium -crf 20 \
      -movflags +faststart "${SAIDA}-${SUFIXO}.mp4"
  fi

  echo ">> pronto: ${SAIDA}-${SUFIXO}.mp4"
}

case "$FORMATO" in
  reels) render 1080 1920 reels ;;
  feed)  render 1080 1350 feed ;;
  ambos) render 1080 1920 reels; render 1080 1350 feed ;;
  *) echo "erro: formato invalido"; exit 64 ;;
esac
