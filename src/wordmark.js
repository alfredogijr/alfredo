// Monta o wordmark: texto em Comfortaa + "r" desenhado à mão (SVG) no estilo
// do novo logotipo do Instagram. Usado dentro da página que o render.mjs abre.
const R_PATHS = {
  // "r" de arco geométrico — legível, mantém a leitura de "grão de mostarda"
  arco: 'M8 92 V50 C8 38 20 32 34 32 C46 32 52 38 52 46',
  // "r" espelhado (o meme do "Instagzam") — piada da trend
  espelhado: 'M6 34 H46 C52 34 54 40 50 46 L14 92 H54',
};

function glyphR(style, stroke) {
  return `<svg class="r" viewBox="0 -8 62 108" aria-hidden="true"><path d="${R_PATHS[style]}" `
       + `fill="none" stroke="currentColor" stroke-width="${stroke}" `
       + `stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}

// Troca todo "r" do texto pelo glifo desenhado.
function wordmark(text, style, stroke = 8) {
  if (style === 'none') return text;
  return text.split('r').join(glyphR(style, stroke));
}
