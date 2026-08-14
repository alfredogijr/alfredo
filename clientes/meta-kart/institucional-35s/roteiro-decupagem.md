# Meta Kart — institucional 35s

Roteiro de edição fechado. Ritmo acelerado, cortes secos, trilha instrumental
energética sem vocal, texto branco em negrito centralizado na parte inferior.

Duração total: **35,00s** — 20 cortes, 8 blocos.

## Decupagem

Os 8 blocos do briefing foram subdivididos em cortes para sustentar o ritmo
acelerado. As durações de bloco e os textos são exatamente os do briefing.

| Bloco | Tempo | Cortes | Texto na tela |
|---|---|---|---|
| 1 | 0:00–0:03 | 3 × 1,0s — Norte → Barra → Campo Grande | Três pistas. Uma só experiência. |
| 2 | 0:03–0:08 | 2,6s plano aberto (zoom leve) + 2,4s kart cruzando | No NorteShopping, você encontra a pista mais longa do Rio de Janeiro. |
| 3 | 0:08–0:13 | 2,5s entrada no túnel + 2,5s close nas luzes (zoom leve) | Na Barra, o único túnel de LED do Rio de Janeiro te leva pra outro nível. |
| 4 | 0:13–0:18 | 2,4s curvas técnicas + 2,6s ultrapassagem | Em Campo Grande, um traçado técnico que exige leitura e precisão em cada curva. |
| 5 | 0:18–0:22 | 4 cortes acelerando: 1,3 → 1,1 → 0,9 → 0,7s | Três estruturas. Uma só referência em kart indoor. |
| 6 | 0:22–0:27 | 1,8 + 1,6 + 1,6s — salão, convidados, mesa posta | Espaço pensado pra receber você e seus convidados antes, durante e depois da corrida. |
| 7 | 0:27–0:31 | 1,4 + 1,3 + 1,3s — chegada, troféu, abraços | Cada detalhe pensado pra transformar seu evento em uma experiência completa. |
| 8 | 0:31–0:35 | 4,0s logo sobre fundo escuro (zoom leve) + fade out | Reserve sua próxima corrida pelo WhatsApp. |

O bloco 5 acelera o corte de 1,3s para 0,7s — é o ponto de virada entre a parte
de pista e a parte de eventos. O fade out final começa em 0:34,4.

A lista corte a corte, com arquivo de origem e timecode de entrada, está em
`remotion/src/decupagem.ts` — que é a fonte única de verdade da peça.

## Texto na tela

- Montserrat 800, branco puro, centralizado na parte inferior.
- Fundo preto semitransparente a 65% (estilo `caixa`, padrão). A variante
  `sombra` sai pela prop `estiloLegenda`.
- Entrada e saída com fade de 150ms, para não piscar em cima do corte.
- Margem inferior: 7,8% da altura no 16x9 e 14% no 9x16 (o vertical sobe o texto
  para escapar da interface do Instagram e do WhatsApp).

Dois pontos que ajustei e valem confirmação:

1. **Capitalização de nomes próprios.** O briefing veio em caixa baixa
   ("norteshopping", "barra", "campo grande"); na tela usei NorteShopping,
   Barra, Campo Grande e LED. O conteúdo do texto está intacto.
2. **Densidade do bloco 7.** "Cada detalhe pensado pra transformar seu evento em
   uma experiência completa." são 75 caracteres em 4s (~19 caracteres por
   segundo), acima do confortável para leitura. Mantive como está porque o
   briefing pediu o texto exato — mas se quiser aliviar, cortar "pensado"
   resolve sem perder o sentido.

## Transições

Cortes secos em todas as emendas. O leve zoom in (até 8% ao longo do corte)
entra em 4 planos: 2.1, 3.2, 6.1 e 8. Nenhum outro efeito.

## Trilha

O briefing pede instrumental energética sem vocal. **Não há trilha definida
ainda** — o material próprio não inclui uma faixa licenciada para isso.

O que existe no Drive é o áudio `KART vs DRONE FPV ... .m4a`, que é rip de vídeo
do YouTube e não serve para peça institucional. Antes de fechar o vídeo é
preciso escolher uma faixa com licença comercial. Referência de busca: eletrônica
instrumental, 120–128 BPM, build contínuo, sem queda de energia até os 0:31 e
resolução no final. O script aplica fade out de 1s a partir de 0:34.

Coloque a faixa em `remotion/public/fontes/trilha.m4a` e passe o nome na prop
`trilha` — o volume já cai em fade de 1s no final.

## Como renderizar

A peça é um projeto Remotion. Instruções completas em
[`remotion/README.md`](remotion/README.md).

```bash
cd remotion
npm install
npm run studio     # preview com timeline
npx remotion render Institucional-16x9 out/PROVA-tempo-16x9.mp4   # prova de tempo
```

Para a peça final, com o material bruto em `remotion/public/fontes/`:

```bash
npx remotion render Institucional-16x9 out/institucional-16x9.mp4 \
  --props='{"modo":"real","estiloLegenda":"caixa","trilha":"trilha.m4a"}'
```

## Fonte tipográfica

As legendas saem em Montserrat 800, empacotada no projeto via `@fontsource`, sem
depender do que está instalado na máquina que renderiza. Para trocar pela fonte
de marca do Meta Kart, ajuste o `fontFamily` em `remotion/src/Legenda.tsx` e
adicione o `@font-face` correspondente.
