/**
 * Identidade visual do vídeo institucional B2B da Meta Kart.
 *
 * ATENÇÃO: as cores abaixo são um ponto de partida (preto + vermelho de corrida).
 * Troque pelos valores do manual de marca da Meta Kart antes de renderizar a
 * versão final.
 */
export const theme = {
  bg: "#050505",
  accent: "#E10600",
  text: "#FFFFFF",
  textMuted: "rgba(255, 255, 255, 0.72)",

  // Stack de fontes do sistema para o projeto rodar em qualquer máquina sem
  // depender de download. Se a Meta Kart tiver fonte própria, instale-a e
  // troque aqui.
  fontFamily: '"Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif',
  fontFamilyDisplay:
    '"Archivo Black", "Anton", Impact, "Haettenschwiler", "Arial Black", sans-serif',

  /**
   * Logo da Meta Kart. Coloque o PNG com fundo transparente em `public/` e
   * escreva o nome do arquivo aqui (ex.: "meta-kart-logo.png").
   * Enquanto for `null`, o vídeo escreve "META KART" em texto.
   */
  logo: null as string | null,

  /**
   * Trilha sonora. Coloque o arquivo em `public/` e escreva o nome aqui
   * (ex.: "trilha.mp3"). Use música licenciada — o vídeo será exibido
   * comercialmente numa reunião.
   */
  music: null as string | null,
  musicVolume: 0.35,
} as const;
