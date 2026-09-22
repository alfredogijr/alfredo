# Roteiro do vídeo — Campeonato Meta Kart, 13ª etapa

Vídeo de 30 segundos montado com as fotos da pasta da etapa. Doze cenas de
2,96 segundos, transição em crossfade de meio segundo, zoom lento em cada
foto. O arco é preparação, disputa e pódio: a ordem das fotos importa tanto
quanto o texto.

## Linha do tempo

| # | entra em | texto na tela | que foto colocar |
|---|---|---|---|
| 1 | 0,0s | 13ª ETAPA / META KART | abertura forte, kart em movimento ou grid cheio |
| 2 | 2,5s | Tem quem corra / pelo troféu | troféu, pódio ou piloto concentrado |
| 3 | 4,9s | e tem quem corra / pela curva perfeita | kart inclinado na curva |
| 4 | 7,4s | O grid fecha / e o mundo lá fora some | grid formado, visto de frente ou de cima |
| 5 | 9,8s | São minutos / de decisão pura | largada ou primeira curva |
| 6 | 12,3s | Cada décimo / custa suor | detalhe de piloto, mão no volante, capacete |
| 7 | 14,8s | Ninguém entrega / posição de graça | dois karts lado a lado |
| 8 | 17,2s | O capacete esconde o rosto / não esconde a vontade | close de capacete |
| 9 | 19,7s | Errou a freada? / A próxima curva cobra | disputa, ultrapassagem, roda a roda |
| 10 | 22,1s | No fim, o pódio / é de poucos | pódio com os três |
| 11 | 24,6s | A história / é de todo mundo | foto de grupo, box, galera |
| 12 | 27,0s | META KART / A próxima largada / já tem data | melhor foto da etapa, fecha em alta |

Os textos ficam no arquivo `textos-13a-etapa.txt`, uma cena por linha, com
`|` separando as quebras. Mudar o texto é mudar essa linha e rodar de novo.

## Como gerar

```bash
cd operacional/video-etapa
./gerar-video.sh -p ~/Downloads/13a-etapa -t textos-13a-etapa.txt -o meta-kart-13a
```

Renomeie as fotos com prefixo numérico na ordem da tabela acima
(`01-grid.jpg`, `02-trofeu.jpg`) antes de rodar, porque o script usa ordem
alfabética.

## Legenda para o post

> A 13ª etapa passou e o que fica não é só o resultado na planilha.
>
> É a freada no limite, a curva que saiu redonda, o décimo que apareceu
> na última volta. Quem estava na pista sabe do que a gente está falando.
>
> Obrigado a todo mundo que fez essa etapa acontecer. A próxima já está
> chegando.
>
> #metakart #kart #kartismo #automobilismo #corrida #velocidade #pista #kartodromo

Ajuste as hashtags para as que o perfil já usa. Se o campeonato tem
hashtag própria de temporada, ela entra no lugar de uma das genéricas.

## Trilha

O script aceita `-m trilha.mp3`, corta no tempo do vídeo e aplica fade de
entrada e saída. Para Instagram, o caminho mais seguro é subir o vídeo sem
áudio e escolher a música dentro do app, que evita bloqueio por direitos e
ainda entrega alcance no som em alta.
