// LA Beauty Concept: everything specific to the salon lives here.
export const LOGO_LIGHT = "https://media.base44.com/images/public/6af5f8bd42323419634c6867/ad44ff4de_logo-paper.png";
export const LOGO_DARK = "https://media.base44.com/images/public/6af5f8bd42323419634c6867/34f8dc694_logo-ink.png";

export const PHOTOS = [
  { image: "https://media.base44.com/images/public/6af5f8bd42323419634c6867/dd4b5fca3_trabalho-02-loiro-dourado-600.webp", label: "Loiro dourado" },
  { image: "https://media.base44.com/images/public/6af5f8bd42323419634c6867/c7d0ca941_trabalho-01-morena-iluminada-mel-600.webp", label: "Mel" },
  { image: "https://media.base44.com/images/public/6af5f8bd42323419634c6867/9d33d4334_trabalho-08-ruivo-cobre-600.webp", label: "Ruivo cobre" },
];

export const PROFESSIONALS = [
  "Lucas Azevedo",
  "Erik Rodrigues",
  "Ana Clara Miranda",
  "Thaine Mendes",
  "Julia Souza",
  "Kamyla Andrade",
  "Jailson da Silva",
  "Érika Costa",
];

export const SERVICES = [
  "Cor (mechas, morena iluminada, coloração)",
  "Corte",
  "Tratamento",
  "Alinhamento",
  "Escova ou babyliss",
  "Mega hair",
  "Manicure e pedicure",
];

// Example prizes: replace with the salon's real offers before launch.
// color = the salon's colour chart (tones sampled from its own work)
export const PRIZES = [
  { name: "Um corte grátis na compra de qualquer serviço", short: "Corte grátis", emoji: "✂️", color: "#c89b62", weight: 25 },
  { name: "50% em manicure e pedicure na compra de qualquer serviço", short: "50% mãos e pés", emoji: "💅", color: "#8f7458", weight: 25 },
  { name: "30% de desconto na sua próxima tintura", short: "30% tintura", emoji: "🎨", color: "#a8502c", weight: 25 },
  { name: "50% de desconto nas suas próximas mechas", short: "50% mechas", emoji: "✨", color: "#5c4433", weight: 25 },
];

export const COUPON_PREFIX = "LA-";
export const COUPON_DAYS = 30;

// The salon's Google review link (Google Business Profile > "Pedir avaliações").
// While empty, the last screen offers WhatsApp and Instagram instead of redirecting.
export const GOOGLE_REVIEW_URL = "";

export const WHATSAPP_URL = "https://wa.me/5521971585367?text=" + encodeURIComponent("Olá! Ganhei um prêmio na pesquisa e quero agendar meu próximo horário.");
export const INSTAGRAM_URL = "https://www.instagram.com/la.beautyconcept/";

export function firstName(full) {
  return (full || "").split(" ")[0];
}
