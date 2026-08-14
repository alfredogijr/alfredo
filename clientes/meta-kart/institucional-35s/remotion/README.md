# Institucional 35s — projeto Remotion

Peça de 35s do Meta Kart, montada em Remotion (React). O roteiro completo está
em [`../roteiro-decupagem.md`](../roteiro-decupagem.md) e o material de origem em
[`../mapa-de-material.md`](../mapa-de-material.md).

## Rodando

```bash
npm install
npm run studio          # preview interativo, com timeline
```

O Studio abre a timeline com os 20 cortes nomeados por bloco, então dá pra
arrastar o playhead e conferir o sincronismo de cada legenda.

## Renderizando

```bash
# prova de tempo: placas no lugar do bruto, legendas reais
npx remotion render Institucional-16x9 out/PROVA-tempo-16x9.mp4

# peça final, com o material em public/fontes
npx remotion render Institucional-16x9 out/institucional-16x9.mp4 \
  --props='{"modo":"real","estiloLegenda":"caixa","trilha":"trilha.m4a"}'

# vertical
npx remotion render Institucional-9x16 out/institucional-9x16.mp4 \
  --props='{"modo":"real","estiloLegenda":"caixa","trilha":"trilha.m4a"}'
```

Se o ambiente já tiver um Chromium e você quiser evitar que o Remotion baixe
outro, aponte para ele:

```bash
export REMOTION_BROWSER=/caminho/para/chrome
```

## Propriedades da composição

| Prop | Valores | O que faz |
|---|---|---|
| `modo` | `prova` \| `real` | `prova` usa placas cinza no lugar do material bruto. |
| `estiloLegenda` | `caixa` \| `sombra` | `caixa` = fundo preto a 65%. `sombra` = só sombra projetada. |
| `trilha` | nome do arquivo | Arquivo em `public/fontes`. Vazio = sem trilha. |

## Estrutura

| Arquivo | Papel |
|---|---|
| `src/decupagem.ts` | Fonte única de verdade: tempos, textos e os 20 cortes. |
| `src/Institucional.tsx` | Monta a timeline, o zoom, o fade final e a trilha. |
| `src/Legenda.tsx` | Texto na tela conforme o briefing. |
| `src/Placa.tsx` | Placa do modo prova. |
| `src/Root.tsx` | Registra as composições 16x9 e 9x16. |

`decupagem.ts` valida na carga que a soma dos cortes fecha exatamente 35s — se
você mudar uma duração sem compensar em outra, o build quebra com a mensagem
dizendo quantos frames sobraram ou faltaram.

## Material bruto

Vai em `public/fontes/`, com os nomes de `../mapa-de-material.md`. Não é
versionado — são centenas de MB por arquivo.
