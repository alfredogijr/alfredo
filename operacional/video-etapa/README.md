# Vídeo de fotos com transição e texto

Pipeline em ffmpeg para transformar a pasta de fotos de uma etapa em vídeo
de 30 segundos, com zoom lento, transição em crossfade e texto queimado.
Sai em 9:16 (Reels) e 4:5 (feed) na mesma rodada.

## O que você precisa

1. **ffmpeg** instalado (`brew install ffmpeg` no Mac, `sudo apt install ffmpeg` no Linux).
2. As fotos numa pasta local. No Drive: abrir a pasta da etapa, selecionar tudo,
   botão direito, Fazer download. O Drive entrega um .zip, é só descompactar.
3. Opcional: um .mp3 de trilha.

## Como rodar

```bash
./gerar-video.sh -p ~/Downloads/13a-etapa -t textos-13a-etapa.txt -o meta-kart-13a
```

Com trilha e só Reels:

```bash
./gerar-video.sh -p ~/Downloads/13a-etapa -t textos-13a-etapa.txt \
  -o meta-kart-13a -m trilha.mp3 -f reels
```

Saída: `meta-kart-13a-reels.mp4` (1080x1920) e `meta-kart-13a-feed.mp4` (1080x1350).

### Opções

| flag | o que faz | padrão |
|---|---|---|
| `-p` | pasta com as fotos, usadas em ordem alfabética | obrigatório |
| `-t` | arquivo de textos, uma cena por linha, `\|` quebra linha | obrigatório |
| `-o` | nome base da saída | `video` |
| `-d` | duração total em segundos | `30` |
| `-x` | duração da transição | `0.5` |
| `-f` | `reels`, `feed` ou `ambos` | `ambos` |
| `-F` | caminho de um .ttf próprio | DejaVu Sans Bold |
| `-m` | trilha sonora | sem áudio |

## Controlando a edição

**Ordem das fotos** é a ordem alfabética do nome do arquivo. Para mandar na
sequência, renomeie com prefixo numérico: `01-largada.jpg`, `02-grid.jpg`.
A ordem importa: o roteiro de texto foi escrito para um arco de preparação,
disputa e pódio.

**Quantidade de fotos** define o ritmo. Em 30 segundos:

| fotos | tempo por foto | sensação |
|---|---|---|
| 8 | 3,7s | contemplativo, cada imagem respira |
| 12 | 2,5s | equilibrado, é o padrão do roteiro |
| 15 | 2,0s | acelerado, combina com corrida |
| 20 | 1,5s | quase videoclipe, texto fica difícil de ler |

O script trava se a conta deixar cada foto com menos de 0,9s.

**Textos**: cada linha do arquivo é uma cena, na mesma ordem das fotos. Linha
vazia é ignorada. Se tiver menos texto que foto, sobra foto sem cena e o
script corta o excesso. Escreva curto: duas linhas de até 25 caracteres
ficam legíveis no celular.

## Ajustes finos

O texto fica a 13% da altura a partir da base, com caixa preta a 42% de
opacidade. Para mexer, editar as variáveis `TAM_TEXTO` e `MARGEM` dentro da
função `render`, ou a linha do `drawtext`.

A transição padrão é `fade`. O ffmpeg aceita outras no mesmo lugar:
`fadeblack`, `wiperight`, `slideup`, `circleopen`, `dissolve`. Trocar em
`transition=fade` dentro do `FILTRO`.

O zoom lento (efeito Ken Burns) está em `zoompan=z='min(zoom+0.0007,1.12)'`.
Aumentar o `0.0007` deixa o movimento mais agressivo, o `1.12` é o limite de
aproximação.

## Desempenho

Referência de máquina modesta: 12 fotos em 30 segundos, nos dois formatos,
levam cerca de 1 minuto de render. O gargalo é o zoom, não a quantidade de
fotos.

## Armadilha do zoompan (já resolvida aqui)

O filtro `zoompan` gera `d` frames para **cada** frame que entra. Se a foto
entrar com `-loop 1 -t 3`, são 90 frames de entrada virando 90 clipes de 90
frames, e o vídeo sai com minutos em vez de segundos. Por isso o script
passa a foto como frame único e controla a duração pelo `-frames:v`.
