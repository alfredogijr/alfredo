#!/usr/bin/env bash
# Baixa e instancia as fontes necessárias para o renderer.
# Executar uma vez antes de rodar o pipeline (ou no step de setup do GitHub Actions).
set -euo pipefail

FONTS_DIR="$(dirname "$0")/fonts"
SPECIAL_GOTHIC_SRC="$(dirname "$0")/../identidade-visual/fontes/Special_Gothic_Expanded_One/SpecialGothicExpandedOne-Regular.ttf"

mkdir -p "$FONTS_DIR"

# Special Gothic — copiar do repositório (já incluso)
if [ ! -f "$FONTS_DIR/SpecialGothic.ttf" ]; then
    cp "$SPECIAL_GOTHIC_SRC" "$FONTS_DIR/SpecialGothic.ttf"
    echo "Special Gothic copiada."
fi

# Montserrat variable font
if [ ! -f "$FONTS_DIR/Montserrat.ttf" ]; then
    curl -sL "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf" \
         -o "$FONTS_DIR/Montserrat.ttf"
    echo "Montserrat variable baixada."
fi

# Instanciar SemiBold (peso 600) da variable font
if [ ! -f "$FONTS_DIR/Montserrat-SemiBold.ttf" ]; then
    python3 -c "
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
f = TTFont('$FONTS_DIR/Montserrat.ttf')
instantiateVariableFont(f, {'wght': 600}).save('$FONTS_DIR/Montserrat-SemiBold.ttf')
"
    echo "Montserrat SemiBold instanciada."
fi

echo "Fontes OK."
