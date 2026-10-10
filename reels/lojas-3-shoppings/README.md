# Reel: nossas lojas em 3 shoppings

Reel 9:16 (1080x1920, ~26 s) feito em Remotion: mapa real do Rio, caminho animado
Shopping Metropolitano Barra → NorteShopping → Park Shopping Campo Grande, uma parada
por loja com endereço e fechamento com os três pontos no mapa.

- Marca, cores, textos, endereços e coordenadas: `src/config.ts`
- Logo: coloque em `public/` e preencha `BRAND.logo`
- Mapa: `data/rio-region.json` (limites municipais do RJ, click_that_hood, simplificados)
- Sem trilha: a música entra no app do Instagram

```bash
npm i
npm run studio   # prévia
npm run render   # out/reel-lojas-3-shoppings.mp4
```
