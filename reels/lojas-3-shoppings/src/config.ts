// Tudo que muda de cliente para cliente fica aqui: marca, cores, textos e lojas.

export const BRAND = {
  name: "SUA MARCA", // trocar pelo nome (ou usar LOGO abaixo)
  logo: "", // ex.: "logo.png" dentro de public/ — se vazio, mostra o nome em texto
  handle: "@seuperfil",
  colors: {
    sea: "#121a24", // fundo (mar)
    land: "#1d2733", // municípios vizinhos
    city: "#26323f", // cidade do Rio
    accent: "#c9a86a", // rota, pins e destaques
    light: "#e8d9b8",
    text: "#ffffff",
  },
  font: "Montserrat",
};

export const TEXTS = {
  hookEyebrow: "Onde estamos",
  hookTitle: "Três shoppings.\n*Três regiões do Rio.*",
  finalEyebrow: "Escolha a mais perto de você",
  finalTitle: "shoppings no Rio",
  endTagline: "Barra, Zona Norte\ne Zona Oeste.",
};

export type Store = {
  name: string;
  address: string;
  district: string;
  lon: number;
  lat: number;
  labelSide: "left" | "right";
};

// Ordem do trajeto. Coordenadas aproximadas (centro de cada shopping).
export const STORES: Store[] = [
  {
    name: "Shopping Metropolitano Barra",
    address: "Av. Embaixador Abelardo Bueno, 1300",
    district: "Barra da Tijuca",
    lon: -43.3727,
    lat: -22.9745,
    labelSide: "left",
  },
  {
    name: "NorteShopping",
    address: "Av. Dom Hélder Câmara, 5474",
    district: "Cachambi",
    lon: -43.2829,
    lat: -22.8866,
    labelSide: "left",
  },
  {
    name: "Park Shopping Campo Grande",
    address: "Estrada do Monteiro, 1200",
    district: "Campo Grande",
    lon: -43.548,
    lat: -22.888,
    labelSide: "right",
  },
];

// Pontos intermediários de cada trecho (lon, lat), só para a curva ficar natural no mapa.
export const LEGS: [number, number][][] = [
  [
    [-43.3727, -22.9745],
    [-43.356, -22.952],
    [-43.336, -22.93],
    [-43.31, -22.906],
    [-43.29, -22.891],
    [-43.2829, -22.8866],
  ],
  [
    [-43.2829, -22.8866],
    [-43.305, -22.868],
    [-43.36, -22.852],
    [-43.43, -22.853],
    [-43.5, -22.866],
    [-43.548, -22.888],
  ],
];

// Referências no mapa (só orientação visual)
export const PLACES: [string, number, number][] = [
  ["Barra da Tijuca", -43.35, -23.006],
  ["Recreio", -43.47, -23.017],
  ["Jacarepaguá", -43.37, -22.94],
  ["Tijuca", -43.235, -22.928],
  ["Centro", -43.18, -22.904],
  ["Copacabana", -43.19, -22.968],
  ["Madureira", -43.34, -22.873],
  ["Bangu", -43.465, -22.872],
  ["Santa Cruz", -43.69, -22.915],
  ["Guaratiba", -43.585, -22.99],
  ["Ilha do Governador", -43.2, -22.8],
  ["Duque de Caxias", -43.31, -22.775],
  ["Niterói", -43.09, -22.9],
];
