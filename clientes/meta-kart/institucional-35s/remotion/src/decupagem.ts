/**
 * Decupagem do institucional de 35s do Meta Kart.
 *
 * Este arquivo é a fonte única de verdade da peça: tempos, textos e cortes.
 * Mexer aqui muda o vídeo inteiro. Os tempos de bloco e os textos vieram
 * fechados no briefing e não devem mudar.
 */

export const FPS = 30;
export const DURACAO_TOTAL = 35; // segundos

export const seg = (s: number) => Math.round(s * FPS);

/** Bloco do briefing: uma legenda cobrindo uma faixa de tempo. */
export type Bloco = {
  inicio: number;
  fim: number;
  /** Uma entrada por linha na tela. As quebras são intencionais. */
  linhas: string[];
};

export const BLOCOS: Bloco[] = [
  { inicio: 0, fim: 3, linhas: ["Três pistas. Uma só experiência."] },
  {
    inicio: 3,
    fim: 8,
    linhas: ["No NorteShopping, você encontra", "a pista mais longa do Rio de Janeiro."],
  },
  {
    inicio: 8,
    fim: 13,
    linhas: ["Na Barra, o único túnel de LED", "do Rio de Janeiro te leva pra outro nível."],
  },
  {
    inicio: 13,
    fim: 18,
    linhas: ["Em Campo Grande, um traçado técnico que", "exige leitura e precisão em cada curva."],
  },
  {
    inicio: 18,
    fim: 22,
    linhas: ["Três estruturas.", "Uma só referência em kart indoor."],
  },
  {
    inicio: 22,
    fim: 27,
    linhas: ["Espaço pensado pra receber você e seus", "convidados antes, durante e depois da corrida."],
  },
  {
    inicio: 27,
    fim: 31,
    linhas: ["Cada detalhe pensado pra transformar", "seu evento em uma experiência completa."],
  },
  { inicio: 31, fim: 35, linhas: ["Reserve sua próxima corrida pelo WhatsApp."] },
];

/** Um corte da timeline. */
export type Corte = {
  bloco: number;
  /** Arquivo dentro de public/fontes/. Ver mapa-de-material.md. */
  arquivo: string;
  /** Ponto de entrada no arquivo de origem, em segundos. A CONFERIR no bruto. */
  entrada: number;
  /** Duração do corte na peça final, em segundos. Fechada. */
  duracao: number;
  /** Leve zoom in ao longo do corte. */
  zoom: boolean;
  descricao: string;
};

export const CORTES: Corte[] = [
  // Bloco 1 — montagem rápida das três pistas, uma atrás da outra.
  { bloco: 1, arquivo: "norte.mp4", entrada: 12, duracao: 1.0, zoom: false, descricao: "Plano geral da pista do NorteShopping" },
  { bloco: 1, arquivo: "barra.mp4", entrada: 10, duracao: 1.0, zoom: false, descricao: "Plano geral da pista da Barra" },
  { bloco: 1, arquivo: "campo-grande.mp4", entrada: 8, duracao: 1.0, zoom: false, descricao: "Plano geral da pista de Campo Grande" },

  // Bloco 2 — NorteShopping, a pista mais longa.
  { bloco: 2, arquivo: "norte.mp4", entrada: 26, duracao: 2.6, zoom: true, descricao: "Plano aberto mostrando a extensão do circuito" },
  { bloco: 2, arquivo: "norte.mp4", entrada: 48, duracao: 2.4, zoom: false, descricao: "Kart em alta velocidade cruzando o quadro" },

  // Bloco 3 — Barra, o túnel de LED.
  { bloco: 3, arquivo: "barra.mp4", entrada: 34, duracao: 2.5, zoom: false, descricao: "Kart entrando no túnel de LED" },
  { bloco: 3, arquivo: "barra.mp4", entrada: 41, duracao: 2.5, zoom: true, descricao: "Close no efeito visual das luzes em movimento" },

  // Bloco 4 — Campo Grande, traçado técnico.
  { bloco: 4, arquivo: "campo-grande.mp4", entrada: 22, duracao: 2.4, zoom: false, descricao: "Sequência de curvas técnicas" },
  { bloco: 4, arquivo: "campo-grande.mp4", entrada: 37, duracao: 2.6, zoom: false, descricao: "Kart fazendo ultrapassagem" },

  // Bloco 5 — o corte acelera de 1,3s para 0,7s. Virada da peça.
  { bloco: 5, arquivo: "norte.mp4", entrada: 60, duracao: 1.3, zoom: false, descricao: "Flash da pista do NorteShopping" },
  { bloco: 5, arquivo: "barra.mp4", entrada: 55, duracao: 1.1, zoom: false, descricao: "Flash da pista da Barra" },
  { bloco: 5, arquivo: "campo-grande.mp4", entrada: 50, duracao: 0.9, zoom: false, descricao: "Flash da pista de Campo Grande" },
  { bloco: 5, arquivo: "onboard.mp4", entrada: 90, duracao: 0.7, zoom: false, descricao: "Flash onboard, ponto de vista do piloto" },

  // Bloco 6 — estrutura para eventos.
  { bloco: 6, arquivo: "festa-01.mp4", entrada: 5, duracao: 1.8, zoom: true, descricao: "Salão de festas montado, mesas prontas" },
  { bloco: 6, arquivo: "festa-02.mp4", entrada: 3, duracao: 1.6, zoom: false, descricao: "Convidados confraternizando antes da corrida" },
  { bloco: 6, arquivo: "festa-03.mp4", entrada: 7, duracao: 1.6, zoom: false, descricao: "Mesa posta, detalhe da estrutura do salão" },

  // Bloco 7 — clima de vitória.
  { bloco: 7, arquivo: "podio-01.mp4", entrada: 4, duracao: 1.4, zoom: false, descricao: "Comemoração na linha de chegada" },
  { bloco: 7, arquivo: "podio-02.mp4", entrada: 2, duracao: 1.3, zoom: false, descricao: "Troféu erguido" },
  { bloco: 7, arquivo: "podio-03.mp4", entrada: 6, duracao: 1.3, zoom: false, descricao: "Abraços, clima de vitória" },

  // Bloco 8 — assinatura.
  { bloco: 8, arquivo: "encerramento.mp4", entrada: 0, duracao: 4.0, zoom: true, descricao: "Logo Meta Kart sobre fundo escuro, karts desfocados ao fundo" },
];

/** Frame em que cada corte começa, acumulado na ordem da timeline. */
export const inicioDoCorte = (indice: number): number =>
  CORTES.slice(0, indice).reduce((total, c) => total + seg(c.duracao), 0);

/** Confere se a soma dos cortes fecha os 35s. Roda no carregamento do módulo. */
const somaDosCortes = CORTES.reduce((total, c) => total + seg(c.duracao), 0);
if (somaDosCortes !== seg(DURACAO_TOTAL)) {
  throw new Error(
    `A decupagem soma ${somaDosCortes} frames e deveria somar ${seg(DURACAO_TOTAL)}. ` +
      `Ajuste as durações em CORTES.`,
  );
}
