/**
 * MetaKartRankingCard.jsx
 * ─────────────────────────────────────────────────────────────────────────────
 * Componente React completo para geração e exportação do card de ranking
 * semanal Meta Kart Indoor Karting.
 *
 * DEPENDÊNCIAS (instale no projeto Base44):
 *   npm install html2canvas @fontsource/bebas-neue @fontsource/montserrat
 *
 * USO:
 *   import MetaKartRankingCard from './MetaKartRankingCard';
 *
 *   <MetaKartRankingCard
 *     track="barra"           // "barra" | "norte" | "campo_grande"
 *     format="instagram"      // "instagram" | "tv"
 *     category="ATÉ 75KG"     // "ATÉ 75KG" | "DE 75KG A 90KG" | "ACIMA 90KG"
 *     period="25/05/2026 a 31/05/2026"
 *     entries={[
 *       { pos: 1, name: "CARLOS SILVA",    time: "31.245" },
 *       { pos: 2, name: "PEDRO SANTOS",    time: "31.892" },
 *       ...
 *     ]}
 *     logoUrl="/logo_metakart_white.png"
 *   />
 */

import React, { useCallback } from 'react';

// ─── Importação de fontes (coloque isso no _app.jsx ou index.jsx do projeto) ───
// import '@fontsource/bebas-neue';
// import '@fontsource/montserrat/400.css';
// import '@fontsource/montserrat/600.css';
// import '@fontsource/montserrat/700.css';
// Se não usar @fontsource, inclua o link no HTML:
// <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">

// ─── Configuração de pistas ────────────────────────────────────────────────────
const TRACK_CONFIG = {
  barra: {
    name:          'BARRA',
    primary:       '#6C34C8',
    primaryDark:   '#30125F',
    primaryLight:  '#B980FF',
    bg:            '#3C1982',
    rowBg:         '#5226A5',
    numBg:         '#280C5A',
    gradientFrom:  '#1a0838',
    gradientVia:   '#3C1982',
    gradientTo:    '#5226A5',
  },
  norte: {
    name:          'NORTE',
    primary:       '#169630',
    primaryDark:   '#08370E',
    primaryLight:  '#3CD758',
    bg:            '#0E551E',
    rowBg:         '#146E28',
    numBg:         '#083712',
    gradientFrom:  '#041A07',
    gradientVia:   '#0E551E',
    gradientTo:    '#146E28',
  },
  campo_grande: {
    name:          'CAMPO GRANDE',
    primary:       '#FD8330',
    primaryDark:   '#A04100',
    primaryLight:  '#FFB45F',
    bg:            '#D25508',
    rowBg:         '#AF4400',
    numBg:         '#823200',
    gradientFrom:  '#3D1200',
    gradientVia:   '#D25508',
    gradientTo:    '#AF4400',
  },
};

// ─── Hierarquia de pódio ───────────────────────────────────────────────────────
const PODIUM = {
  1: { accent: '#D4AF37', label: 'gold'   }, // Ouro F1 championship
  2: { accent: '#A8A9AD', label: 'silver' }, // Prata pódio
  3: { accent: '#CD7F32', label: 'bronze' }, // Bronze pódio
};

// ─── Dimensões dos formatos ────────────────────────────────────────────────────
const FORMATS = {
  instagram: { width: 1080, height: 1350, label: 'Instagram (1080×1350)' },
  tv:        { width: 1920, height: 1080, label: 'TV Wide (1920×1080)'   },
};

// ─── Utilitários ──────────────────────────────────────────────────────────────

/** Interpola entre duas cores hex */
function lerpHex(a, b, t) {
  const parse = (h) => {
    const v = h.replace('#', '');
    return [
      parseInt(v.slice(0, 2), 16),
      parseInt(v.slice(2, 4), 16),
      parseInt(v.slice(4, 6), 16),
    ];
  };
  const ca = parse(a), cb = parse(b);
  const r = Math.round(ca[0] + (cb[0] - ca[0]) * t);
  const g = Math.round(ca[1] + (cb[1] - ca[1]) * t);
  const bv = Math.round(ca[2] + (cb[2] - ca[2]) * t);
  return `rgb(${r},${g},${bv})`;
}

// ─── Linha de ranking (parallelogram + podium hierarchy) ─────────────────────

function RankingRow({ entry, cfg, format, rowHeight, isLast }) {
  const isPodium = entry.pos <= 3;
  const isP1     = entry.pos === 1;
  const podium   = PODIUM[entry.pos];

  // Zebra striping para P4-P10: posições pares ficam ligeiramente mais escuras
  const isZebraAlt = !isPodium && entry.pos % 2 === 0;

  // Largura do badge de posição proporcional à altura
  const numBadgeW  = isP1 ? rowHeight * 0.88 : rowHeight * 0.80;
  // Inclinação do parallelogram em px (22% da altura — estilo F1 timing board)
  const slant      = Math.round(rowHeight * 0.22);
  // Espessura da faixa de acento colorido (ouro/prata/bronze ou cor da pista)
  const stripeW    = isP1 ? 14 : isPodium ? 10 : 5;

  // Cores da faixa de posição e fundo da linha
  const accentColor = podium
    ? podium.accent
    : cfg.primaryLight;

  // Fundo da linha: gradiente horizontal suave
  // Zebra: linhas pares (P4,P6,P8,P10) recebem um fundo ~12% mais escuro
  const baseRowBg   = isZebraAlt ? lerpHex(cfg.rowBg, cfg.numBg, 0.25) : cfg.rowBg;
  const rowBgLeft  = isPodium
    ? isP1
      ? lerpHex(cfg.primaryLight, '#ffffff', 0.30)
      : lerpHex(cfg.primaryLight, cfg.primary, 0.15)
    : baseRowBg;
  const rowBgRight = isPodium
    ? lerpHex(cfg.primary, cfg.numBg, 0.20)
    : lerpHex(baseRowBg, cfg.numBg, 0.40);

  // Cor do texto do tempo: dourado no P1 (destaque championship), primaryLight nos demais
  const timeColor  = isP1 ? PODIUM[1].accent : cfg.primaryLight;

  // Tamanho da fonte de nome: maior no P1
  const nameFontSize   = format === 'tv'
    ? (isP1 ? 22 : isPodium ? 20 : 17)
    : (isP1 ? Math.round(rowHeight * 0.36) : Math.round(rowHeight * 0.30));
  const numFontSize    = format === 'tv'
    ? (isP1 ? 42 : isPodium ? 36 : 30)
    : Math.round(rowHeight * 0.75);
  const timeFontSize   = format === 'tv'
    ? (isP1 ? 22 : isPodium ? 20 : 17)
    : (isP1 ? Math.round(rowHeight * 0.26) : Math.round(rowHeight * 0.32));

  const rowStyle = {
    position:   'relative',
    height:     rowHeight,
    marginBottom: isLast ? 0 : format === 'tv' ? 6 : 5,
    flexShrink: 0,
  };

  // clip-path do parallelogram: skewX equivalente usando polygon
  // polygon(slant 0, 100% 0, calc(100% - slant) 100%, 0 100%)
  const paraClip = `polygon(${slant}px 0, 100% 0, calc(100% - ${slant}px) 100%, 0 100%)`;

  return (
    <div style={rowStyle}>
      {/* Fundo da linha — parallelogram com gradiente */}
      <div style={{
        position:   'absolute',
        inset:      `0 0 0 0`,
        background: `linear-gradient(90deg, ${rowBgLeft}, ${rowBgRight})`,
        clipPath:   paraClip,
      }} />

      {/* Shine sutil no topo para P1/P2/P3 — efeito metalizado */}
      {isPodium && (
        <div style={{
          position:   'absolute',
          top:        0,
          left:       0,
          right:      0,
          height:     isP1 ? '45%' : '25%',
          background: `linear-gradient(180deg, rgba(255,255,255,${isP1 ? 0.12 : 0.07}) 0%, transparent 100%)`,
          clipPath:   paraClip,
          pointerEvents: 'none',
        }} />
      )}

      {/* Faixa lateral de acento: ouro/prata/bronze ou cor da pista */}
      <div style={{
        position:  'absolute',
        top:       0,
        left:      0,
        width:     slant + stripeW,
        height:    '100%',
        clipPath:  `polygon(${slant}px 0, ${slant + stripeW}px 0, ${stripeW}px 100%, 0 100%)`,
        background: accentColor,
        zIndex:    2,
      }} />

      {/* Badge do número de posição (fundo escuro da pista) */}
      <div style={{
        position:  'absolute',
        top:       0,
        left:      0,
        width:     numBadgeW + slant,
        height:    '100%',
        clipPath:  `polygon(${slant}px 0, ${numBadgeW + slant}px 0, ${numBadgeW}px 100%, 0 100%)`,
        background: cfg.numBg,
        zIndex:    1,
      }} />

      {/* Número da posição — Bebas Neue dominante */}
      <div style={{
        position:   'absolute',
        top:        0,
        left:       slant + stripeW + 2,
        width:      numBadgeW - stripeW - 2,
        height:     '100%',
        display:    'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex:     3,
      }}>
        <span style={{
          fontFamily:  "'Bebas Neue', 'BebasNeue-Regular', Impact, sans-serif",
          fontSize:    numFontSize,
          color:       podium ? podium.accent : '#ffffff',
          lineHeight:  1,
          letterSpacing: '0.02em',
          textShadow: isP1
            ? `0 0 ${Math.round(numFontSize * 0.4)}px ${cfg.primaryLight}88, 0 0 ${Math.round(numFontSize * 0.8)}px ${cfg.primaryLight}44`
            : 'none',
        }}>
          {entry.pos}
        </span>
      </div>

      {/* Conteúdo principal: nome + líder de pontos + tempo */}
      <div style={{
        position:   'absolute',
        top:        0,
        left:       numBadgeW + slant + (format === 'tv' ? 18 : 14),
        right:      slant + (format === 'tv' ? 28 : 24),
        height:     '100%',
        display:    'flex',
        alignItems: 'center',
        gap:        0,
        zIndex:     3,
      }}>
        {/* Nome do piloto */}
        <span style={{
          fontFamily:  "'Montserrat', sans-serif",
          fontSize:    nameFontSize,
          fontWeight:  isPodium ? 700 : 600,
          color:       '#ffffff',
          whiteSpace:  'nowrap',
          overflow:    'hidden',
          textOverflow: 'ellipsis',
          flex:        '0 1 auto',
          maxWidth:    '65%',
          letterSpacing: isP1 ? '0.05em' : isPodium ? '0.03em' : '0.025em',
        }}>
          {entry.name}
        </span>

        {/* Líder de pontos animado (dots) */}
        <div style={{
          flex:     1,
          minWidth: format === 'tv' ? 20 : 16,
          margin:   `0 ${format === 'tv' ? 10 : 8}px`,
          display:  'flex',
          alignItems: 'center',
          overflow: 'hidden',
        }}>
          <DotLeader color={lerpHex(cfg.primaryLight, rowBgRight, 0.60)} />
        </div>

        {/* Tempo — fonte monospace para alinhamento preciso */}
        <span style={{
          fontFamily:  "'Montserrat', 'Courier New', monospace",
          fontSize:    timeFontSize,
          fontWeight:  700,
          color:       timeColor,
          whiteSpace:  'nowrap',
          flexShrink:  0,
          letterSpacing: '0.06em',
          fontVariantNumeric: 'tabular-nums',
        }}>
          {entry.time}
        </span>
      </div>
    </div>
  );
}

/** Líder de pontos — linha de dots semi-transparentes */
function DotLeader({ color }) {
  return (
    <div style={{
      width:    '100%',
      height:   4,
      display:  'flex',
      alignItems: 'center',
      gap:      6,
      overflow: 'hidden',
    }}>
      {/* Renderiza ~30 dots; o overflow:hidden corta automaticamente */}
      {Array.from({ length: 32 }).map((_, i) => (
        <div
          key={i}
          style={{
            width:     3,
            height:    3,
            borderRadius: '50%',
            background: color,
            flexShrink: 0,
            opacity:   0.75,
          }}
        />
      ))}
    </div>
  );
}

// ─── Speed Lines de fundo (efeito de velocidade) ──────────────────────────────

function SpeedLines({ primaryLight, count = 14 }) {
  // Posições fixas (seed determinístico para consistência entre renders)
  const lines = Array.from({ length: count }, (_, i) => {
    const seed = i * 137.508; // golden angle para distribuição uniforme
    const yPct = ((seed * 2.39) % 100);
    const height = 1 + (i % 3);
    // Opacidade aumentada: mínimo 0.10, máximo 0.28 — visível no PNG exportado
    const opacity = 0.10 + (i % 4) * 0.045;
    const xOffset = (i % 2 === 0) ? '-5%' : '-10%';
    return { yPct, height, opacity, xOffset };
  });

  return (
    <div style={{
      position:      'absolute',
      inset:         0,
      pointerEvents: 'none',
      overflow:      'hidden',
    }}>
      {lines.map((l, i) => (
        <div
          key={i}
          style={{
            position:   'absolute',
            top:        `${l.yPct}%`,
            left:       l.xOffset,
            right:      '-5%',
            height:     l.height,
            background: `linear-gradient(90deg, transparent, ${primaryLight}${Math.round(l.opacity * 255).toString(16).padStart(2, '0')}, transparent)`,
          }}
        />
      ))}
    </div>
  );
}

// ─── Halftone dots overlay (assinatura visual da marca) ───────────────────────

function HalftoneDots() {
  return (
    <div style={{
      position:      'absolute',
      inset:         0,
      pointerEvents: 'none',
      // SVG inline como background para halftone sem canvas
      backgroundImage: `radial-gradient(circle, rgba(255,255,255,0.08) 1.5px, transparent 1.5px)`,
      backgroundSize: '20px 20px',
    }} />
  );
}

// ─── Separador de pódio (linha antes do P4) ───────────────────────────────────

function PodiumSeparator({ cfg, format }) {
  return (
    <div style={{
      width:      '100%',
      height:     1,
      background: `linear-gradient(90deg, transparent, ${cfg.primaryLight}55, transparent)`,
      margin:     `${format === 'tv' ? 2 : 3}px 0`,
      flexShrink: 0,
    }} />
  );
}

// ─── Layout Instagram (1080×1350) ─────────────────────────────────────────────

function RankingCardInstagram({ cfg, category, entries, period, logoUrl, scale }) {
  // Dimensões base em px (design a 1080×1350, escaladas pelo scale)
  const W = 1080, H = 1350;

  // Alturas das linhas com hierarquia de pódio
  // P1: 1.42x  P2: 1.14x  P3: 1.06x  P4+: 1.0x
  // Área disponível: H - topBar(10) - header(~96) - sep(4) - footer(88) - gaps(9*5)
  const topBarH    = 14;
  const headerH    = 110;
  const sepH       = 4;
  const footerH    = 88;
  const rowGap     = 5;
  const available  = H - topBarH - headerH - sepH - footerH - (9 * rowGap);
  const baseRowH   = Math.max(80, Math.round((available) / (1.42 + 1.14 + 1.06 + 7.0)));
  const rowHeights = {
    1: Math.round(baseRowH * 1.42),
    2: Math.round(baseRowH * 1.14),
    3: Math.round(baseRowH * 1.06),
  };
  const getRowH = (pos) => rowHeights[pos] || baseRowH;

  const hPad = 44; // padding horizontal das linhas e header

  return (
    <div style={{
      position:   'relative',
      width:      W,
      height:     H,
      overflow:   'hidden',
      transform:  `scale(${scale})`,
      transformOrigin: 'top left',
      fontFamily: "'Montserrat', sans-serif",
      // Fundo escuro com gradiente vertical da cor da pista
      background: `linear-gradient(180deg, ${cfg.gradientFrom} 0%, ${cfg.gradientVia} 45%, ${cfg.gradientTo} 100%)`,
    }}>
      {/* Glow radial central — profundidade fotográfica */}
      <div style={{
        position:     'absolute',
        top:          '25%',
        left:         '50%',
        transform:    'translate(-50%, -50%)',
        width:        '140%',
        paddingBottom: '140%',
        borderRadius: '50%',
        background:   `radial-gradient(circle, ${cfg.primary}38 0%, transparent 70%)`,
        pointerEvents: 'none',
      }} />

      {/* Halftone dots (assinatura visual da marca) */}
      <HalftoneDots />

      {/* Speed lines de fundo */}
      <SpeedLines primaryLight={cfg.primaryLight} count={18} />

      {/* Barra superior de acento */}
      <div style={{
        position:   'absolute',
        top:        0,
        left:       0,
        right:      0,
        height:     topBarH,
        background: cfg.primaryLight,
      }} />

      {/* Header: título esquerda + badge de categoria direita */}
      <div style={{
        position:   'absolute',
        top:        topBarH + 12,
        left:       hPad,
        right:      hPad,
        height:     headerH - 12,
        display:    'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Título */}
        <span style={{
          fontFamily:  "'Bebas Neue', Impact, sans-serif",
          fontSize:    76,
          color:       '#ffffff',
          lineHeight:  1,
          letterSpacing: '0.04em',
        }}>
          RANKING DA SEMANA
        </span>

        {/* Badge de categoria — chevron estilo motorsport */}
        <CategoryBadge label={category} cfg={cfg} />
      </div>

      {/* Separador de header */}
      <div style={{
        position:   'absolute',
        top:        topBarH + headerH,
        left:       hPad,
        right:      hPad,
        height:     2,
        background: `${cfg.primaryLight}55`,
      }} />

      {/* Linhas de ranking */}
      <div style={{
        position:   'absolute',
        top:        topBarH + headerH + sepH + 28,
        left:       hPad,
        right:      hPad,
        bottom:     footerH,
        display:    'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}>
        {entries.map((entry, i) => (
          <React.Fragment key={entry.pos}>
            {entry.pos === 4 && <PodiumSeparator cfg={cfg} format="instagram" />}
            <RankingRow
              entry={entry}
              cfg={cfg}
              format="instagram"
              rowHeight={getRowH(entry.pos)}
              isLast={i === entries.length - 1}
            />
          </React.Fragment>
        ))}
      </div>

      {/* Footer: logo + período */}
      <div style={{
        position:   'absolute',
        bottom:     0,
        left:       0,
        right:      0,
        height:     footerH,
        display:    'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap:        4,
      }}>
        {logoUrl && (
          <img
            src={logoUrl}
            alt="Meta Kart"
            crossOrigin="anonymous"
            style={{
              maxWidth:  period ? 170 : 210,
              maxHeight: period ? 46  : 62,
              objectFit: 'contain',
              filter:    'brightness(0) invert(1)',
            }}
          />
        )}
        {period && (
          <span style={{
            fontFamily:    "'Montserrat', sans-serif",
            fontSize:      18,
            fontWeight:    600,
            color:         'rgba(220,220,240,0.75)',
            letterSpacing: '0.04em',
          }}>
            {period}
          </span>
        )}
        <span style={{
          fontFamily:    "'Montserrat', sans-serif",
          fontSize:      13,
          fontWeight:    700,
          color:         `${cfg.primaryLight}88`,
          letterSpacing: '0.10em',
        }}>
          #METAKART
        </span>
      </div>

      {/* Barra inferior de acento */}
      <div style={{
        position:   'absolute',
        bottom:     0,
        left:       0,
        right:      0,
        height:     10,
        background: cfg.primary,
      }} />
    </div>
  );
}

// ─── Layout TV Wide (1920×1080) ───────────────────────────────────────────────

function RankingCardTV({ cfg, category, entries, period, logoUrl, scale }) {
  const W = 1920, H = 1080;
  const topBarH  = 12;
  const sidebarW = 272;

  // Alturas das linhas para TV
  const baseRowH = 72;
  const getRowH  = (pos) => {
    if (pos === 1) return Math.round(baseRowH * 1.38);
    if (pos === 2) return Math.round(baseRowH * 1.12);
    if (pos === 3) return Math.round(baseRowH * 1.05);
    return baseRowH;
  };

  const contentX = sidebarW + 72;
  const contentW = W - contentX - 36;
  const hdrH     = 74;

  return (
    <div style={{
      position:   'relative',
      width:      W,
      height:     H,
      overflow:   'hidden',
      transform:  `scale(${scale})`,
      transformOrigin: 'top left',
      fontFamily: "'Montserrat', sans-serif",
      background: `linear-gradient(160deg, ${cfg.gradientFrom} 0%, ${cfg.gradientVia} 50%, ${cfg.gradientTo} 100%)`,
    }}>
      {/* Glow radial */}
      <div style={{
        position:     'absolute',
        top:          '40%',
        left:         '55%',
        transform:    'translate(-50%, -50%)',
        width:        '120%',
        paddingBottom: '90%',
        borderRadius: '50%',
        background:   `radial-gradient(circle, ${cfg.primary}30 0%, transparent 65%)`,
        pointerEvents: 'none',
      }} />

      <HalftoneDots />
      <SpeedLines primaryLight={cfg.primaryLight} count={16} />

      {/* Barra superior */}
      <div style={{
        position:   'absolute',
        top:        0,
        left:       0,
        right:      0,
        height:     topBarH,
        background: cfg.primaryLight,
      }} />

      {/* Sidebar esquerda — sobreposição escura gradiente */}
      <div style={{
        position:   'absolute',
        top:        0,
        left:       0,
        width:      sidebarW + 60,
        height:     H,
        background: `linear-gradient(90deg, rgba(0,0,0,0.72) ${sidebarW - 40}px, transparent)`,
        pointerEvents: 'none',
        zIndex:     2,
      }} />

      {/* Sidebar — logo, nome da pista, período */}
      <div style={{
        position:   'absolute',
        top:        topBarH,
        left:       0,
        width:      sidebarW,
        height:     H - topBarH - 7,
        display:    'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex:     3,
      }}>
        {/* Logo */}
        {logoUrl && (
          <img
            src={logoUrl}
            alt="Meta Kart"
            crossOrigin="anonymous"
            style={{
              maxWidth:  Math.round(sidebarW * 0.80),
              maxHeight: Math.round(sidebarW * 0.32),
              objectFit: 'contain',
              filter:    'brightness(0) invert(1)',
              marginBottom: 20,
            }}
          />
        )}

        {/* Nome da pista */}
        {cfg.name.split(' ').map((word, i) => (
          <span key={i} style={{
            fontFamily:  "'Bebas Neue', Impact, sans-serif",
            fontSize:    58,
            color:       '#ffffff',
            lineHeight:  1.05,
            letterSpacing: '0.04em',
            textAlign:   'center',
          }}>
            {word}
          </span>
        ))}

        {/* Separador */}
        <div style={{
          width:     '60%',
          height:    2,
          background: cfg.primaryLight,
          margin:    '14px 0',
          opacity:   0.6,
        }} />

        {/* Período */}
        {period && (
          <div style={{
            fontFamily:  "'Montserrat', sans-serif",
            fontSize:    14,
            color:       'rgba(220,220,240,0.85)',
            textAlign:   'center',
            lineHeight:  1.5,
            padding:     '0 12px',
            whiteSpace:  'pre-line',
          }}>
            {period.replace(' a ', '\n')}
          </div>
        )}
      </div>

      {/* Área de conteúdo — header + linhas */}
      <div style={{
        position:   'absolute',
        top:        topBarH,
        left:       contentX,
        width:      contentW,
        bottom:     7,
        zIndex:     3,
      }}>
        {/* Header linha 1: título + badge */}
        <div style={{
          height:     hdrH,
          display:    'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <span style={{
            fontFamily:  "'Bebas Neue', Impact, sans-serif",
            fontSize:    64,
            color:       '#ffffff',
            lineHeight:  1,
            letterSpacing: '0.04em',
          }}>
            RANKING DA SEMANA
          </span>
          <CategoryBadge label={category} cfg={cfg} size="tv" />
        </div>

        {/* Separador de header + labels de colunas */}
        <div style={{ position: 'relative', height: 32 }}>
          <div style={{
            position:   'absolute',
            top:        0,
            left:       0,
            right:      0,
            height:     3,
            background: cfg.primary,
          }} />
          <div style={{
            position:   'absolute',
            bottom:     0,
            left:       0,
            right:      0,
            display:    'flex',
            justifyContent: 'space-between',
            padding:    '0 2px',
          }}>
            <span style={{
              fontFamily: "'Montserrat', sans-serif",
              fontSize:   15,
              color:      'rgba(180,180,200,0.85)',
              fontWeight: 400,
              letterSpacing: '0.08em',
              paddingLeft: Math.round(baseRowH * 0.80) + 36,
            }}>
              COMPETIDOR
            </span>
            <span style={{
              fontFamily: "'Montserrat', sans-serif",
              fontSize:   15,
              color:      'rgba(180,180,200,0.85)',
              fontWeight: 400,
              letterSpacing: '0.08em',
              paddingRight: Math.round(baseRowH * 0.22) + 20,
            }}>
              TEMPO
            </span>
          </div>
        </div>

        {/* Linhas de ranking */}
        <div style={{
          display:       'flex',
          flexDirection: 'column',
          paddingTop:    6,
        }}>
          {entries.map((entry, i) => (
            <React.Fragment key={entry.pos}>
              {entry.pos === 4 && <PodiumSeparator cfg={cfg} format="tv" />}
              <RankingRow
                entry={entry}
                cfg={cfg}
                format="tv"
                rowHeight={getRowH(entry.pos)}
                isLast={i === entries.length - 1}
              />
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Barra inferior */}
      <div style={{
        position:   'absolute',
        bottom:     0,
        left:       0,
        right:      0,
        height:     7,
        background: cfg.primary,
      }} />
    </div>
  );
}

// ─── Badge de Categoria ────────────────────────────────────────────────────────

function CategoryBadge({ label, cfg, size = 'instagram' }) {
  const fontSize  = size === 'tv' ? 26 : 22;
  const padX      = size === 'tv' ? 20 : 18;
  const padY      = size === 'tv' ? 8  : 10;
  // Clip chevron (estilo designação de classe motorsport)
  const h         = fontSize + padY * 2;
  const chevron   = Math.round(h * 0.35);

  return (
    <div style={{
      position:   'relative',
      display:    'inline-flex',
      alignItems: 'center',
      flexShrink: 0,
    }}>
      <span style={{
        display:    'inline-block',
        background: cfg.primary,
        clipPath:   `polygon(${chevron}px 0, 100% 0, calc(100% - ${chevron}px) 100%, 0 100%)`,
        padding:    `${padY}px ${padX + chevron / 2}px`,
        fontFamily: "'Montserrat', sans-serif",
        fontSize:   fontSize,
        fontWeight: 700,
        color:      '#ffffff',
        letterSpacing: '0.06em',
        whiteSpace: 'nowrap',
      }}>
        {label}
      </span>
    </div>
  );
}

// ─── Painel de controles de export ────────────────────────────────────────────

function ExportPanel({ cardProps, format, track, category }) {
  const [exporting, setExporting] = React.useState(false);

  const handleExport = useCallback(async () => {
    setExporting(true);

    // Referências declaradas fora do try para o finally poder limpá-las
    let offscreen = null;
    let root      = null;

    try {
      const html2canvas               = (await import('html2canvas')).default;
      const { createRoot }            = await import('react-dom/client');
      const { width, height }         = FORMATS[format];
      const CardComponent             = format === 'tv' ? RankingCardTV : RankingCardInstagram;

      // ── 1. Wrapper invisível no topo do document (não usa posição negativa).
      //       visibility:hidden mantém o layout intacto sem mostrar ao usuário.
      //       O wrapper tem as dimensões exatas do card — html2canvas captura
      //       o elemento passado diretamente, sem depender de coordenadas absolutas.
      const wrapper = document.createElement('div');
      wrapper.style.cssText = [
        'position:absolute',
        'top:0',
        'left:0',
        `width:${width}px`,
        `height:${height}px`,
        'overflow:hidden',
        'visibility:hidden',
        'pointer-events:none',
        'z-index:-9999',
      ].join(';');
      document.body.appendChild(wrapper);
      offscreen = wrapper;

      // ── 2. Renderiza o card em escala 1:1 (sem nenhum CSS transform).
      root = createRoot(offscreen);
      await new Promise((resolve) => {
        root.render(
          React.createElement(CardComponent, {
            ...cardProps,
            scale: 1,
          })
        );
        // 400ms: React concurrent mode flush + imagens inline (logo dataURL)
        setTimeout(resolve, 400);
      });

      // Aguarda fontes do documento (Bebas Neue + Montserrat)
      if (document.fonts?.ready) await document.fonts.ready;

      // ── 3. Captura com html2canvas.
      //       • Não passamos x/y/scrollX/scrollY — deixa o html2canvas localizar
      //         o elemento pelo bounding rect real dele no DOM.
      //       • windowWidth/windowHeight = dimensões do card, não da tela,
      //         para que vh/vw resolvam corretamente dentro do card.
      //       • scale:1 → canvas pixels = DOM pixels (sem HiDPI artificioso).
      const canvas = await html2canvas(offscreen, {
        width,
        height,
        scale:           1,
        useCORS:         true,
        allowTaint:      false,
        logging:         false,
        backgroundColor: null,
        windowWidth:     width,
        windowHeight:    height,
        onclone: (clonedDoc, clonedEl) => {
          // Remove visibility:hidden do clone para o html2canvas enxergar o conteúdo
          clonedEl.style.visibility = 'visible';

          // Injeta as fontes no documento clonado caso ainda não existam
          if (!clonedDoc.querySelector('link[href*="googleapis"]')) {
            const link = clonedDoc.createElement('link');
            link.rel   = 'stylesheet';
            link.href  = 'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;600;700&display=swap';
            clonedDoc.head.appendChild(link);
          }
        },
      });

      // Valida dimensões — falha rápida se o canvas saiu menor que o esperado
      if (canvas.width !== width || canvas.height !== height) {
        console.warn(
          `[MetaKart export] Canvas ${canvas.width}×${canvas.height} difere do esperado ${width}×${height}. Verifique o DPR do browser.`
        );
      }

      // ── 4. Download
      const trackSlug = track.replace(/_/g, '-');
      const catSlug   = category
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[àáâã]/g, 'a')
        .replace(/[éê]/g, 'e');
      const filename = `metakart_${trackSlug}_${catSlug}_${format}.png`;

      await new Promise((resolve, reject) => {
        canvas.toBlob((blob) => {
          if (!blob) { reject(new Error('toBlob retornou null — verifique CORS do logo.')); return; }
          const url = URL.createObjectURL(blob);
          const a   = document.createElement('a');
          a.href     = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          setTimeout(() => { URL.revokeObjectURL(url); resolve(); }, 100);
        }, 'image/png', 1.0);
      });

    } catch (err) {
      console.error('[MetaKart export]', err);
      alert(`Erro ao exportar: ${err.message}`);
    } finally {
      // Cleanup garantido — root e offscreen declarados no escopo da função
      try { root?.unmount(); } catch (_) {}
      if (offscreen && document.body.contains(offscreen)) {
        document.body.removeChild(offscreen);
      }
      setExporting(false);
    }
  }, [cardProps, format, track, category]);

  const { width, height } = FORMATS[format];

  return (
    <div style={{
      display:      'flex',
      alignItems:   'center',
      gap:          12,
      padding:      '12px 16px',
      background:   '#1a1a2e',
      borderTop:    '1px solid rgba(255,255,255,0.1)',
      borderRadius: '0 0 8px 8px',
    }}>
      <span style={{
        color:      'rgba(255,255,255,0.5)',
        fontSize:   13,
        fontFamily: 'monospace',
      }}>
        {width}×{height}px · PNG
      </span>
      <button
        onClick={handleExport}
        disabled={exporting}
        style={{
          marginLeft:  'auto',
          padding:     '8px 20px',
          background:  exporting
            ? 'rgba(108,52,200,0.4)'
            : 'linear-gradient(135deg, #6C34C8, #B980FF)',
          border:      'none',
          borderRadius: 6,
          color:       exporting ? 'rgba(255,255,255,0.5)' : '#fff',
          fontFamily:  "'Montserrat', sans-serif",
          fontSize:    14,
          fontWeight:  700,
          cursor:      exporting ? 'wait' : 'pointer',
          letterSpacing: '0.06em',
          transition:  'all 0.2s',
        }}
      >
        {exporting ? 'GERANDO...' : 'EXPORTAR PNG'}
      </button>
    </div>
  );
}

// ─── Componente Principal Exportado ───────────────────────────────────────────

/**
 * @param {object} props
 * @param {'barra'|'norte'|'campo_grande'} props.track
 * @param {'instagram'|'tv'} props.format
 * @param {string} props.category  - "ATÉ 75KG" | "DE 75KG A 90KG" | "ACIMA 90KG"
 * @param {string} props.period    - ex: "25/05/2026 a 31/05/2026"
 * @param {Array<{pos:number,name:string,time:string}>} props.entries
 * @param {string} props.logoUrl   - URL do logo Meta Kart (PNG com fundo transparente)
 */
// ─── Dados de demonstração ────────────────────────────────────────────────────
// Declarado ANTES do componente para evitar ReferenceError (const não sofre hoisting)
export const DEMO_ENTRIES = [
  { pos: 1,  name: 'CARLOS SILVA',     time: '31.245' },
  { pos: 2,  name: 'PEDRO SANTOS',     time: '31.892' },
  { pos: 3,  name: 'JOAO COSTA',       time: '32.100' },
  { pos: 4,  name: 'ANA LIMA',         time: '32.450' },
  { pos: 5,  name: 'MARCOS OLIVEIRA',  time: '32.811' },
  { pos: 6,  name: 'RAFAEL GOMES',     time: '33.120' },
  { pos: 7,  name: 'LUCAS FERREIRA',   time: '33.490' },
  { pos: 8,  name: 'GABRIEL SOUZA',    time: '33.721' },
  { pos: 9,  name: 'MATEUS BARBOSA',   time: '34.010' },
  { pos: 10, name: 'THIAGO CARVALHO',  time: '34.350' },
];

export default function MetaKartRankingCard({
  track    = 'barra',
  format   = 'instagram',
  category = 'ATÉ 75KG',
  period   = '',
  entries  = DEMO_ENTRIES,
  logoUrl  = null,
}) {
  const cfg = TRACK_CONFIG[track];

  if (!cfg) return <div style={{ color: 'red' }}>Pista inválida: {track}</div>;

  const { width, height } = FORMATS[format];
  const CardComponent     = format === 'tv' ? RankingCardTV : RankingCardInstagram;

  // Scale para preview — calculado aqui e passado para o card
  const previewMaxW = typeof window !== 'undefined'
    ? Math.min(window.innerWidth * 0.90, 860)
    : 860;
  const previewMaxH = typeof window !== 'undefined'
    ? window.innerHeight * 0.72
    : 580;
  const scaleByW     = previewMaxW / width;
  const scaleByH     = previewMaxH / height;
  const previewScale = Math.min(scaleByW, scaleByH, 1);

  // cardProps é passado ao ExportPanel para que ele possa re-renderizar
  // o card em resolução completa num container offscreen antes de capturar.
  const cardProps = { cfg, category, entries, period, logoUrl };

  return (
    <div
      style={{
        display:       'flex',
        flexDirection: 'column',
        alignItems:    'flex-start',
        gap:           0,
        fontFamily:    "'Montserrat', sans-serif",
      }}
    >
      {/* Preview escalado para o browser — transform no wrapper interno,
          não no card, para não quebrar o box model do layout pai */}
      <div style={{
        width:        Math.round(width  * previewScale),
        height:       Math.round(height * previewScale),
        overflow:     'hidden',
        position:     'relative',
        borderRadius: '4px 4px 0 0',
        boxShadow:    '0 4px 32px rgba(0,0,0,0.7)',
        flexShrink:   0,
      }}>
        <div style={{
          width:           width,
          height:          height,
          transform:       `scale(${previewScale})`,
          transformOrigin: 'top left',
          marginRight:  -(width  - Math.round(width  * previewScale)),
          marginBottom: -(height - Math.round(height * previewScale)),
        }}>
          <CardComponent
            {...cardProps}
            scale={1}
          />
        </div>
      </div>

      {/* Painel de export — usa container offscreen em resolução real */}
      <ExportPanel
        cardProps={cardProps}
        format={format}
        track={track}
        category={category}
      />
    </div>
  );
}

// ─── Página de preview completa (para uso no Base44 como rota /ranking) ───────

/**
 * RankingPreviewPage
 *
 * Página completa com seletor de pista/formato/categoria e upload de logo.
 * Cole isso no Base44 como uma página ou substitua MetaKartRankingCard diretamente.
 */
export function RankingPreviewPage() {
  const [track,    setTrack]    = React.useState('barra');
  const [format,   setFormat]   = React.useState('instagram');
  const [category, setCategory] = React.useState('ATÉ 75KG');
  const [period,   setPeriod]   = React.useState('25/05/2026 a 31/05/2026');
  const [logoUrl,  setLogoUrl]  = React.useState(null);
  const [entries,  setEntries]  = React.useState(DEMO_ENTRIES);

  const cfg = TRACK_CONFIG[track];

  // Upload da logo como data URL
  const handleLogoUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setLogoUrl(ev.target.result);
    reader.readAsDataURL(file);
  };

  // Edição inline de pilotos
  const updateEntry = (pos, field, value) => {
    setEntries(prev => prev.map(e =>
      e.pos === pos ? { ...e, [field]: value } : e
    ));
  };

  const trackOptions = [
    { value: 'barra',        label: 'Barra (Roxo)'    },
    { value: 'norte',        label: 'Norte (Verde)'   },
    { value: 'campo_grande', label: 'Campo Grande (Laranja)' },
  ];
  const formatOptions  = Object.entries(FORMATS).map(([k, v]) => ({ value: k, label: v.label }));
  const categoryOptions = ['ATÉ 75KG', 'DE 75KG A 90KG', 'ACIMA 90KG'];

  const selectStyle = {
    padding:      '8px 12px',
    background:   '#1e1e2e',
    border:       '1px solid rgba(255,255,255,0.15)',
    borderRadius: 6,
    color:        '#fff',
    fontFamily:   "'Montserrat', sans-serif",
    fontSize:     13,
    cursor:       'pointer',
  };
  const labelStyle = {
    color:      'rgba(255,255,255,0.6)',
    fontSize:   12,
    letterSpacing: '0.08em',
    marginBottom: 4,
    display:    'block',
  };
  const inputStyle = {
    ...selectStyle,
    width: '100%',
  };

  return (
    <div style={{
      minHeight:   '100vh',
      background:  '#0d0d1a',
      padding:     '24px 20px',
      display:     'flex',
      flexDirection: 'column',
      gap:         24,
    }}>
      {/* Fontes Google — inclua isso no index.html em produção */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;600;700&display=swap');
        * { box-sizing: border-box; }
      `}</style>

      {/* Título */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{
          width:      6,
          height:     32,
          background: cfg.primaryLight,
          borderRadius: 3,
        }} />
        <span style={{
          fontFamily:  "'Bebas Neue', sans-serif",
          fontSize:    28,
          color:       '#fff',
          letterSpacing: '0.06em',
        }}>
          META KART — GERADOR DE RANKING
        </span>
      </div>

      <div style={{
        display: 'flex',
        gap:     24,
        flexWrap: 'wrap',
        alignItems: 'flex-start',
      }}>
        {/* ── Painel de controles ─────────────────────────────────────────── */}
        <div style={{
          width:        300,
          flexShrink:   0,
          display:      'flex',
          flexDirection: 'column',
          gap:          16,
          background:   '#12122a',
          padding:      20,
          borderRadius: 10,
          border:       '1px solid rgba(255,255,255,0.08)',
        }}>
          <div>
            <label style={labelStyle}>PISTA</label>
            <select
              value={track}
              onChange={e => setTrack(e.target.value)}
              style={{ ...selectStyle, width: '100%' }}
            >
              {trackOptions.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={labelStyle}>FORMATO DE SAÍDA</label>
            <select
              value={format}
              onChange={e => setFormat(e.target.value)}
              style={{ ...selectStyle, width: '100%' }}
            >
              {formatOptions.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={labelStyle}>CATEGORIA</label>
            <select
              value={category}
              onChange={e => setCategory(e.target.value)}
              style={{ ...selectStyle, width: '100%' }}
            >
              {categoryOptions.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={labelStyle}>PERÍODO</label>
            <input
              type="text"
              value={period}
              onChange={e => setPeriod(e.target.value)}
              placeholder="dd/mm/aaaa a dd/mm/aaaa"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={labelStyle}>LOGO (PNG transparente)</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleLogoUpload}
              style={{ ...inputStyle, padding: '6px 8px' }}
            />
            {logoUrl && (
              <div style={{
                marginTop: 8,
                padding:   8,
                background: 'rgba(255,255,255,0.05)',
                borderRadius: 4,
                display:   'flex',
                alignItems: 'center',
                gap:       8,
              }}>
                <img
                  src={logoUrl}
                  alt="preview"
                  style={{ maxWidth: 80, maxHeight: 30, filter: 'brightness(0) invert(1)' }}
                />
                <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>
                  Logo carregada
                </span>
              </div>
            )}
          </div>

          {/* ── Editor de pilotos ────────────────────────────────────────── */}
          <div>
            <label style={{ ...labelStyle, marginBottom: 10 }}>PILOTOS</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {entries.map(e => (
                <div key={e.pos} style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <span style={{
                    fontFamily: "'Bebas Neue', sans-serif",
                    fontSize:   18,
                    color:      e.pos <= 3 ? [,'#D4AF37','#A8A9AD','#CD7F32'][e.pos] : 'rgba(255,255,255,0.4)',
                    width:      22,
                    textAlign:  'center',
                    flexShrink: 0,
                  }}>
                    {e.pos}
                  </span>
                  <input
                    value={e.name}
                    onChange={ev => updateEntry(e.pos, 'name', ev.target.value.toUpperCase())}
                    style={{ ...inputStyle, flex: 1, fontSize: 11 }}
                    placeholder="NOME DO PILOTO"
                  />
                  <input
                    value={e.time}
                    onChange={ev => updateEntry(e.pos, 'time', ev.target.value)}
                    style={{ ...inputStyle, width: 72, fontSize: 11, fontFamily: 'monospace' }}
                    placeholder="31.245"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Preview do card ─────────────────────────────────────────────── */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <MetaKartRankingCard
            track={track}
            format={format}
            category={category}
            period={period}
            entries={entries}
            logoUrl={logoUrl}
          />
        </div>
      </div>
    </div>
  );
}
