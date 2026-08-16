# Meta Kart — Vídeo institucional B2B (60s, 16:9)

**Objetivo:** abrir uma reunião com empresários e vender o empreendimento como
lugar para **eventos corporativos** (confraternização, integração de equipe,
incentivo de vendas, ação com clientes).

**Público:** dono de empresa / decisor. Ele não compra adrenalina — compra
equipe integrada, evento sem dor de cabeça e um lugar que impressiona quem ele
convidar.

**Contexto de exibição:** projetado/apresentado no início da reunião, provavelmente
com som ambiente ruim. Por isso: **toda mensagem essencial está em texto na tela**.
O vídeo funciona no mudo.

**Formato de saída:** MP4 H.264, 1920×1080 (16:9), 30 fps, 60s exatos.

---

## Princípio de edição

Nos primeiros 20 segundos o vídeo mostra **o lugar**; nos 20 do meio, **as
pessoas**; nos 20 finais, **a oferta para a empresa dele**. A ordem importa: o
empresário precisa primeiro acreditar na estrutura, depois se ver levando o time.

Ritmo: takes de 4 a 8 segundos, sem corte picotado. Vídeo para empresário é
mais respirado que vídeo de rede social — a pressa passa impressão de amadorismo.

---

## Decupagem

| # | Tempo | Dur. | O que procurar no material bruto | Texto na tela |
|---|---|---|---|---|
| 01 | 00:00–00:04 | 4s | Kart em velocidade máxima passando perto da câmera, largada ou curva fechada. O take mais cinematográfico que existir. Manter som do motor. | — |
| 02 | 00:04–00:07 | 3s | Plano aberto e estável do kartódromo (drone, se houver). Base limpa para a cartela. | **Meta Kart** · Para empresas — *Experiências corporativas em alta velocidade* |
| 03 | 00:07–00:12 | 5s | Aérea ou panorâmica que mostre a **escala**: pista inteira, estacionamento, prédio. | O complexo — *Um espaço preparado para receber grupos* |
| 04 | 00:12–00:17 | 5s | Recepção, lounge, bar, área coberta, mesas. Onde o grupo fica antes e depois de correr. | Estrutura — *Recepção, lounge e área de convivência* |
| 05 | 00:17–00:22 | 5s | Karts alinhados, box, equipe de pista, capacetes, painel de cronometragem. Passa seriedade operacional. | Operação — *Karts e equipe de pista prontos para o seu grupo* |
| 06 | 00:22–00:27 | 5s | Grupo se preparando: briefing, capacete, macacão, gente rindo. **Priorizar adultos** — público de empresa, não criança. | A experiência — *Todo mundo entra no mesmo grid* |
| 07 | 00:27–00:33 | 6s | Melhor ultrapassagem / karts lado a lado / câmera baixa na reta. Pico de energia. Manter som. | *Dez minutos de pista dizem mais que uma dinâmica de grupo* |
| 08 | 00:33–00:40 | 7s | Pódio, comemoração, abraço, gente rindo tirando o capacete. Fecha o arco emocional. | *E vira assunto na segunda-feira* |
| 09 | 00:40–00:46 | 6s | Grupo grande confraternizando fora da pista: mesas, brinde, crachá, camiseta de empresa. | Para sua empresa — *Confraternização, integração e ação com clientes* / Do encontro do time à premiação da força de vendas |
| 10 | 00:46–00:52 | 6s | Pista ou salão ocupados só por um grupo, premiação, troféu, telão. Mostra que o lugar fecha para um cliente só. | Eventos corporativos — *Sua empresa no controle da pista* / Formato fechado, no seu dia e no seu horário |
| 11 | 00:52–01:00 | 8s | Plano bonito de fechamento: pôr do sol na pista, kart parado no grid, fachada iluminada. | **Traga sua equipe para a Meta Kart** + contato |

**Origem dos takes:** os blocos 01–08 devem sair dos três vídeos da pasta
`video institucional`. Os takes 09 e 10 são os mais difíceis de achar lá — se não
existirem, puxe de vídeos de eventos/aniversários/campeonatos já gravados. É neles
que o empresário se enxerga.

---

## Antes de aprovar: confirmar com o cliente

A copy acima é **proposta** e faz afirmações sobre o negócio. Antes de exibir,
confirmar com a Meta Kart:

- [ ] Capacidade real por evento (de quantas a quantas pessoas) — se houver número
      forte, ele entra no take 10 e vale mais que a frase genérica.
- [ ] O que está de fato incluso num evento fechado (premiação, locução,
      cronometragem, buffet, espaço reservado).
- [ ] Se existe pacote/tabela para empresa e se pode ser citado.
- [ ] Telefone, site e nome de quem atende empresa (entra no take 11).
- [ ] Cores e logo oficiais (hoje o projeto está com preto + vermelho genérico).

Regra: **se o take não mostra aquilo, a frase sai.** Texto prometendo estrutura
que a imagem não comprova derruba a credibilidade justamente com esse público.

---

## Como montar

O projeto de edição já está pronto em `video/` (Remotion). Passo a passo:

1. Copie os arquivos escolhidos para `video/public/`.
2. Descubra a duração de cada um: `npx remotion ffprobe public/ARQUIVO.mp4`
3. Abra `video/src/MetaKart/shots.ts` e, em cada take, preencha:
   - `src`: nome do arquivo
   - `trimBeforeInSeconds`: em que segundo do arquivo o take começa
4. Rode `npm run dev` e ajuste vendo o preview ao vivo.
5. Ajuste marca e trilha em `video/src/MetaKart/theme.ts`.
6. Exporte: `npx remotion render MetaKartB2B out/meta-kart-b2b.mp4`

Enquanto `src` estiver vazio, o take aparece como cartela de storyboard — dá para
aprovar a estrutura do filme antes de ter o material cortado.

---

## Checklist antes da reunião

- [ ] Assistir no mudo do começo ao fim: a história se sustenta só com o texto?
- [ ] Assistir com som no volume da sala.
- [ ] Testar no projetor/TV do local (16:9, tela cheia, sem barra preta lateral).
- [ ] Levar o arquivo local, não depender de internet.
- [ ] Ter a resposta pronta para a primeira pergunta que vem depois do vídeo:
      *"quanto custa e quantas pessoas cabem?"*
