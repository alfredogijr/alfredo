# Alfredo — Grão de Mostarda / Turista FC

## Stack de edição de vídeo

- `add_text_overlay.py briefing.json saida.mp4` — engine principal de overlay
- `make_slideshow.py briefing.json saida.mp4` — slideshow de fotos
- `prep_*.py` — scripts de prep para mix foto+vídeo ou áudio específico

## Identidade Turista FC

- **Cor**: `[20, 90, 210]` (azul)
- **Logo**: `/root/.claude/uploads/a2d92e31-73f6-4945-a382-29957624cebe/1c0d3b7b-whitelogo2_transparente_20260601_232004_0000.png`
- **Encerramento padrão**: logo `width_pct: 0.55`, `x_frac: 0.50`, `y_frac: 0.60` + sub `"A sua operadora de turismo esportivo premium."` em `position: "bottom"`
- **Output**: 1080×1920, 30fps, `color_grade: "cinematic"`

---

## Área segura para texto em Reels/Shorts (9:16)

Referência: guia @FlyEnri (YouTube Shorts safe area)

```
┌─────────────────────────────┐  ← topo (0%)
│                             │
│   ZONA SEGURA PRINCIPAL     │
│   (texto principal aqui)    │
│                             │
│                        ███  │  ← botões UI direita (~80–100% largura)
│                        ███  │    like / dislike / comment / share
│                        ███  │    ocupam ~18% da largura direita
│                             │    a partir de ~50% da altura
│  ██████████████████████████ │  ← rodapé UI (~76–100% altura)
│  nome do canal / descrição  │    @handle, título, barra de navegação
└─────────────────────────────┘  ← base (100%)
```

### Regras práticas para posicionamento de texto

| Zona | % da altura | Uso |
|------|-------------|-----|
| `top` (engine) | 8% | Texto principal — livre de UI |
| `center` (engine) | ~45–55% | Texto principal — livre de UI |
| `bottom` (engine) | 76% | Tagline/CTA — limite seguro antes da UI do Instagram |
| **PROIBIDO** | > 80% | Coberto pela barra de navegação |
| **CUIDADO** | > 55% na borda direita | Coberto pelos botões de reação |

### Sobre os botões de reação (lado direito)

- Aparecem a partir de ~50% da altura
- Cobrem ~18% da largura direita
- **Evitar texto alinhado à direita na metade inferior do frame**
- Logo centralizada (`x_frac: 0.50`) é segura pois fica no centro

### Logo Turista FC no encerramento

- `y_frac: 0.60` coloca a logo a 60% da altura (~1152px) — acima da zona de risco
- `position: "bottom"` no engine coloca o texto a 76% — limite seguro
- Resultado: logo + tagline ficam visíveis sem sobreposição de UI

---

## Projetos desta sessão

| Arquivo briefing | Projeto |
|-----------------|---------|
| `briefing_wimbledon_v2.json` | Wimbledon — Nadal×Federer 2008 |
| `briefing_wimbledon_mix.json` | Wimbledon Mix — tela preta + rally |
| `briefing_falbo_copa.json` | Alexandre Falbo × Copa do Mundo 2026 |
| `briefing_hamilton.json` | Lewis Hamilton × Ferrari — superação |
