// Monta o wordmark: texto em Comfortaa + o "r" desenhado à mão, no espírito
// do novo logotipo do Instagram.
//
// O glifo é construído a partir das métricas reais da Comfortaa (medidas com
// _metrics.mjs, em milésimos de em, peso 400) para que o "r" tenha a mesma
// altura-x, a mesma espessura de traço e a mesma largura das letras vizinhas:
const M = {
  avanco: 460,   // largura de avanço do "r" da fonte
  alturaX: 550,  // altura-x
  lateral: 90,   // espaço lateral esquerdo até o traço
  traco: 80,     // espessura do traço
};

const meio = M.traco / 2;
const xStem = M.lateral + meio;              // eixo do traço vertical
const yTopo = meio;                          // topo da altura-x
const yBase = M.alturaX - meio;              // linha de base
const raio = 250;                            // curva do ombro
const xArm = xStem + raio;                   // fim do braço

const R_PATHS = {
  // "r" geométrico: traço vertical + ombro em quarto de círculo, todo dentro
  // da altura-x — mesma presença de um "n" ou "m".
  arco: `M${xStem} ${yBase} V${yTopo + raio} A${raio} ${raio} 0 0 1 ${xArm} ${yTopo}`,
  // "r" espelhado: a piada do "Instagzam", desenhado na mesma caixa.
  espelhado: `M${xArm} ${yTopo} H${xStem} L${xArm} ${yBase} H${xStem}`,
};

function glyphR(style) {
  return `<svg class="r" viewBox="0 0 ${M.avanco} ${M.alturaX}" aria-hidden="true">`
       + `<path d="${R_PATHS[style]}" fill="none" stroke="currentColor" `
       + `stroke-width="${M.traco}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}

// Troca todo "r" do texto pelo glifo desenhado.
function wordmark(text, style) {
  if (style === 'none') return text;
  return text.split('r').join(glyphR(style));
}
