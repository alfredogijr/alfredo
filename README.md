# Grão de Mostarda — Landing page

Página única, animada, focada em **gerar leads / agendar reunião**.
Estilo moderno ("ten thousand / 21st.dev"): hero animado, gradiente vivo,
brilho que segue o mouse, scroll com efeito, contadores e CTA.

## Como ver
Abra o arquivo `index.html` no navegador. Não precisa instalar nada.

## Como publicar (grátis)
- **Netlify Drop**: arraste a pasta em https://app.netlify.com/drop
- **GitHub Pages**: Settings → Pages → branch → `/root`
- **Vercel**: importe o repositório

## Conteúdo
Textos, soluções, resultados e depoimentos são os reais, extraídos do site
oficial (consultoriagrao.com.br). Posicionamento: marketing digital + IA,
foco em dar autonomia ao time interno e reduzir dependência de agências.

## Identidade visual (manual da marca)
- **Cores:** âmbar `#F5A702` (destaque), azul-marinho `#1a2840` / `#0e1828`,
  fundo `#081019`, creme `#F0EDE4`
- **Fontes:** Raleway (títulos) + Inter (texto)
- **Logo:** broto/muda ("o grão que brota") em SVG inline — também no favicon
- **Elemento giratório:** selo circular "GRÃO DE MOSTARDA • MARKETING + IA"
  girando no hero, com broto central que balança (vai e volta)

## Ainda a ajustar
- **Logo oficial em arquivo** (hoje o broto é recriado em SVG a partir do manual;
  se houver um SVG/PNG oficial, é só trocar)
- **Número de WhatsApp** no botão flutuante (hoje aponta pro formulário)
- **Formulário**: abre um e-mail pré-preenchido (mailto). Para captar leads de
  forma automática, ligar a um backend/CRM (ex: Formspree, RD Station, etc.)

## Tecnologias (via CDN, sem build)
- Tailwind CSS · GSAP + ScrollTrigger · Google Fonts (Sora + Inter)
