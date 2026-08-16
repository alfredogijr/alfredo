# grão de mostarda — trend do novo logo do Instagram

Artes prontas pra postar com o nome da agência escrito no estilo do novo
wordmark do Instagram (o mesmo formato que Volkswagen, ChatGPT e cia usaram
na trend de agosto/2025): fundo creme, letra geométrica de traço fino, nome
em caixa baixa ocupando o centro.

## O que tem em `out/`

| arquivo | formato | uso |
|---|---|---|
| `01-feed-wordmark.png` | 1080×1080 | feed — nome em uma linha, `r` desenhado (versão legível) |
| `02-feed-espelhado.png` | 1080×1080 | feed — versão meme, com o `r` espelhado (lê "gzão de mostazda", que é a piada do "Instagzam") |
| `03-feed-duas-linhas.png` | 1080×1080 | feed — nome em duas linhas, presença bem maior |
| `04-feed-mostarda.png` | 1080×1080 | feed — mesma arte no amarelo mostarda |
| `05-feed-slide2.png` | 1080×1080 | segundo slide do carrossel ("instagram novo, grão de mostarda de sempre.") |
| `06-story.png` | 1080×1920 | story |

Sugestão de carrossel: `03` (ou `02`, se for de humor) + `05`.

## Legendas sugeridas

1. novo logo do Instagram, novo jeito de escrever o nosso nome.
   a marca continua a mesma — a fonte que mudou. 🌱
2. o Instagram trocou de fonte e a internet inteira foi escrever o próprio
   nome. a gente também. sem vergonha nenhuma.
3. (pra versão espelhada) juram que tá escrito "grão de mostarda". confia.

Hashtags: #instagram #novoinstagram #branding #design #identidadevisual
#agenciadepublicidade

## Como as letras foram feitas

- Tipografia base: **Comfortaa** (SIL Open Font License 1.1, em
  `assets/fonts/`) — geométrica, monolinear e arredondada, o parente livre
  mais próximo do desenho novo do Instagram.
- O `r` de cada palavra é **desenhado à mão em SVG** (`src/wordmark.js`),
  porque é justamente o `r` esquisito que dá a cara da trend. São dois
  desenhos: `arco` (legível) e `espelhado` (o meme).
- O desenho do `r` sai das **métricas reais da Comfortaa** (altura-x,
  espessura de traço, largura de avanço e espaço lateral), medidas por
  `src/metrics.mjs`. Assim ele tem exatamente o mesmo tamanho e o mesmo peso
  das letras vizinhas — nada de `r` maior ou mais gordo que o resto. Se
  mudar o peso do texto em `src/page.html`, rode `node src/metrics.mjs` de
  novo e atualize as constantes `M` em `src/wordmark.js`.
- A fonte real do Instagram é proprietária e não foi usada nem imitada
  glifo a glifo: isso aqui é uma homenagem/paródia feita com tipografia
  livre, que é o caminho seguro pra uma agência publicar.

## Como regerar / editar

```bash
npm install          # baixa o playwright
npm run build        # gera tudo em out/
```

Onde mexer:
- textos, cores, tamanhos e formatos: array `artes` em `src/render.mjs`
  (`fill` = quanto da largura o texto ocupa, de 0 a 1);
- amarelo da marca: constante `MOSTARDA` em `src/render.mjs` — está em
  `#E3A81C` como aproximação, é só trocar pelo hex oficial da agência;
- pra assinar com o @ da agência, adicione `legenda: '@seuarroba'` na arte
  desejada.
