# Cabine 2 Decks

Mesa de mixagem de dois decks que roda no navegador, feita com Web Audio API.
O app inteiro está em `DJMixer.jsx`, um componente React sem dependências além do próprio React.

## O que tem

- Dois decks com play, pause, CUE no estilo CDJ, pitch (±8, ±16 ou ±50%) e pitch bend
- Detecção automática de BPM e da grade de batidas, com botão SYNC (iguala o andamento e alinha a fase)
- Mixer com ganho, EQ de 3 bandas com KILL por banda, filtro passa-baixa/passa-alta em um botão só, fader de canal e crossfader
- O EQ é um isolador de verdade (cruzamentos Linkwitz-Riley em 250 Hz e 2,5 kHz): o kill zera a banda por completo
- Forma de onda ampliada com grade de batidas e visão geral da faixa, ambas clicáveis
- 4 hot cues e loops automáticos de ½ a 16 batidas por deck
- Medidores de nível por canal e no master, limitador na saída
- Gravação do set (botão REC) com download do arquivo
- Biblioteca de arquivos locais com BPM e duração
- Atalhos de teclado configuráveis: o botão "Atalhos" abre o painel onde cada função pode ganhar outra tecla (fica salvo no navegador)
- Kill por tecla em dois modos: alternar a cada toque ou só enquanto a tecla está apertada
- Troca de grave em uma tecla (Espaço): mata o grave de um deck e devolve o do outro no mesmo instante

## Atalhos padrão

| Função | Deck A | Deck B |
|---|---|---|
| Tocar / pausar | Q | P |
| CUE | W | O |
| SYNC | E | I |
| Kill grave / médio / agudo | A / S / D | J / K / L |
| Hot cues 1 a 4 | 1 2 3 4 | 7 8 9 0 |
| Loop de 4 batidas | R | U |
| Atrasar / adiantar (segurar) | Z / X | N / M |

Mixer: Espaço faz a troca de grave, setas esquerda e direita movem o crossfader, seta para baixo centraliza.

## Como publicar no Base44

1. Crie um app novo no Base44 (pode ser vazio).
2. Crie uma página chamada `DJMixer` e abra o editor de código dela.
3. Substitua todo o conteúdo pelo de `DJMixer.jsx` e salve.
4. Defina essa página como a inicial do app e publique.

Se preferir pelo chat do Base44, peça: "crie uma página DJMixer e use exatamente este código, sem alterar nada" e cole o arquivo.

## Limites conhecidos

- As músicas precisam ser arquivos locais (MP3, WAV, M4A, OGG, FLAC). Spotify e similares não liberam o áudio para mixagem.
- Mudar o pitch muda também o tom da música, como em um toca-discos. Ainda não há key lock.
- Não há pré-escuta no fone em saída separada.
- A biblioteca vive só na sessão do navegador: ao recarregar a página, os arquivos precisam ser adicionados de novo.
