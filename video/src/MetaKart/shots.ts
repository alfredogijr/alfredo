/**
 * DECUPAGEM — Vídeo institucional B2B da Meta Kart (60s, 16:9).
 *
 * Como usar:
 * 1. Copie os arquivos de vídeo bruto para a pasta `public/` deste projeto.
 * 2. Descubra a duração de cada arquivo com:  npx remotion ffprobe public/ARQUIVO.mp4
 * 3. Rode `npm run dev`, abra a composição "MetaKartB2B" e, take a take,
 *    preencha `src` e `trimBeforeInSeconds` abaixo. O preview atualiza sozinho.
 *
 * Enquanto `src` for `null`, o slot aparece como cartela de storyboard —
 * então dá para ver o filme inteiro montado antes mesmo de ter o material.
 *
 * A soma de `durationInSeconds` define a duração do vídeo (hoje: 60s exatos).
 */

export type Overlay = {
  /** lower = texto no rodapé | center = cartela | cta = fechamento */
  kind: "lower" | "center" | "cta";
  kicker?: string;
  headline: string;
  sub?: string;
};

export type Shot = {
  id: string;
  /** O que procurar no material bruto. É o briefing do take. */
  slot: string;
  /** Nome do arquivo dentro de `public/`. `null` = ainda não escolhido. */
  src: string | null;
  /** Segundo do arquivo de origem em que o take começa. */
  trimBeforeInSeconds: number;
  durationInSeconds: number;
  /** Zoom lento. Desligue em takes que já têm movimento de câmera forte. */
  kenBurns?: boolean;
  /** Mantém o áudio original do take (ex.: ronco do motor). */
  keepAudio?: boolean;
  overlay?: Overlay;
};

export const shots: Shot[] = [
  {
    id: "01-gancho",
    slot: "GANCHO: kart em velocidade máxima passando perto da câmera, largada ou curva fechada. O take mais cinematográfico que existir no material.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 4,
    kenBurns: false,
    keepAudio: true,
  },
  {
    id: "02-cartela-abertura",
    slot: "Base para a cartela de abertura: plano aberto e estável do kartódromo (pode ser drone). O texto entra por cima, então evite take poluído.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 3,
    overlay: {
      kind: "center",
      kicker: "Para empresas",
      headline: "Experiências corporativas em alta velocidade",
    },
  },
  {
    id: "03-complexo",
    slot: "O COMPLEXO: plano aéreo ou panorâmica que mostre a escala do empreendimento — pista inteira, estacionamento, prédio.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 5,
    overlay: {
      kind: "lower",
      kicker: "O complexo",
      headline: "Um espaço preparado para receber grupos",
    },
  },
  {
    id: "04-estrutura",
    slot: "ESTRUTURA: recepção, lounge, bar, área coberta, mesas. Tudo que mostre que o grupo tem onde ficar antes e depois de correr.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 5,
    overlay: {
      kind: "lower",
      kicker: "Estrutura",
      headline: "Recepção, lounge e área de convivência",
    },
  },
  {
    id: "05-operacao",
    slot: "OPERAÇÃO: detalhes dos karts alinhados, box, equipe de pista, capacetes, painel de cronometragem. Passa seriedade operacional.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 5,
    overlay: {
      kind: "lower",
      kicker: "Operação",
      headline: "Karts e equipe de pista prontos para o seu grupo",
    },
  },
  {
    id: "06-briefing",
    slot: "A EXPERIÊNCIA: grupo se preparando — briefing, capacete, macacão, gente rindo antes de entrar. De preferência adultos, público de empresa.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 5,
    overlay: {
      kind: "lower",
      kicker: "A experiência",
      headline: "Todo mundo entra no mesmo grid",
    },
  },
  {
    id: "07-disputa",
    slot: "DISPUTA: a melhor ultrapassagem / karts lado a lado / câmera baixa na reta. É o pico de energia do vídeo.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 6,
    kenBurns: false,
    keepAudio: true,
    overlay: {
      kind: "lower",
      headline: "Dez minutos de pista dizem mais que uma dinâmica de grupo",
    },
  },
  {
    id: "08-comemoracao",
    slot: "RESULTADO HUMANO: pódio, comemoração, abraço, gente rindo tirando o capacete. Fecha o arco emocional.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 7,
    overlay: {
      kind: "lower",
      headline: "E vira assunto na segunda-feira",
    },
  },
  {
    id: "09-b2b-ocasioes",
    slot: "B2B: grupo grande confraternizando fora da pista — mesas, brinde, crachá, camiseta de empresa. Se não existir take assim, use o plano mais 'de evento' que houver.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 6,
    overlay: {
      kind: "lower",
      kicker: "Para sua empresa",
      headline: "Confraternização, integração e ação com clientes",
      sub: "Do encontro do time à premiação da força de vendas",
    },
  },
  {
    id: "10-evento-fechado",
    slot: "EVENTO FECHADO: pista ou salão ocupados só pelo grupo, premiação, troféu, telão. Mostra que o empreendimento fecha para um cliente só.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 6,
    overlay: {
      kind: "lower",
      kicker: "Eventos corporativos",
      headline: "Sua empresa no controle da pista",
      sub: "Formato fechado, no seu dia e no seu horário",
    },
  },
  {
    id: "11-cta",
    slot: "FECHAMENTO: o plano mais bonito que sobrou (pôr do sol na pista, kart parado no grid, fachada iluminada). O texto entra por cima.",
    src: null,
    trimBeforeInSeconds: 0,
    durationInSeconds: 8,
    overlay: {
      kind: "cta",
      headline: "Traga sua equipe para a Meta Kart",
    },
  },
];

export const totalDurationInSeconds = shots.reduce(
  (acc, shot) => acc + shot.durationInSeconds,
  0,
);
