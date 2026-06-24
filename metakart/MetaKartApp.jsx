/**
 * MetaKartApp.jsx
 * ─────────────────────────────────────────────────────────────────────────────
 * App completo para o Base44 — combina upload de PDF (parsing client-side),
 * seleção de pista/categoria/formato e exportação de PNG.
 *
 * ARQUITETURA:
 *   1. Usuário faz upload do PDF → pdfjs-dist parseia client-side
 *   2. Regex extrai posição, nome e tempo de cada linha
 *   3. RankingPreviewPage renderiza o card
 *   4. html2canvas exporta como PNG na resolução correta
 *
 * DEPENDÊNCIAS:
 *   npm install pdfjs-dist html2canvas
 *   # Fontes (opcional — também podem ser carregadas via Google Fonts CDN)
 *   npm install @fontsource/bebas-neue @fontsource/montserrat
 *
 * NOTA SOBRE pdf.js worker:
 *   Copie pdf.worker.min.js para /public/pdf.worker.min.js
 *   ou use o CDN: pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/...'
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';

// ─── Re-exporta o componente de card e a página de preview ───────────────────
export { default as MetaKartRankingCard, RankingPreviewPage } from './MetaKartRankingCard';
import MetaKartRankingCard, { DEMO_ENTRIES } from './MetaKartRankingCard';

// ─── Parser de PDF (client-side com pdf.js) ───────────────────────────────────

const TIME_RE   = /\b(\d{2}:\d{2}:\d{3})\b/;
const CAT_MAP   = [
  { re: /A PARTIR DE 90/i,     label: 'ACIMA 90KG'     },
  { re: /AT[EÉ] 75 KG/i,       label: 'ATÉ 75KG'       },
  { re: /DE 75 KG AT[EÉ] 90/i, label: 'DE 75KG A 90KG' },
];
const SKIP_RE   = /RANKING MENSAL|LAPTIME|SISECOM|DATA\/HORA|Competidor|Email|Telefone|Peso|Data|Pista \d|Norte Shopping|Shopping|Página \d|Digitalizado|LapTime|INDOOR KARTING|META KART/i;
const DATE_RE   = /\b(\d{2}\/\d{2}\/\d{4})\b/g;

function fmtTime(raw) {
  const p = raw.split(':');
  return p.length === 3 ? `${p[1]}.${p[2]}` : raw;
}

function extractName(line, stopIdx) {
  const tokens = line.slice(0, stopIdx).split(/\s+/);
  const parts = [];
  for (const tok of tokens) {
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(tok)) break;
    if (tok.includes('@')) break;
    const clean = tok.replace(/[\s\-\(\)\+\.]/g, '');
    if (clean.length >= 7 && /^\d+$/.test(clean)) break;
    if (/^[a-z][a-z0-9._]{9,}$/.test(tok)) break;
    parts.push(tok);
  }
  const name = parts.join(' ').trim();
  return name.length >= 3 ? name.toUpperCase() : '';
}

function parseLines(lines) {
  const sections = {};
  const dates    = [];
  let cur        = null;

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;

    let cat = null;
    for (const { re, label } of CAT_MAP) {
      if (re.test(line)) { cat = label; break; }
    }
    if (cat) { cur = cat; sections[cur] = sections[cur] || []; continue; }
    if (!cur || SKIP_RE.test(line)) continue;

    const tm = TIME_RE.exec(line);
    if (!tm) continue;

    let m;
    const dre = new RegExp(DATE_RE.source, 'g');
    while ((m = dre.exec(line)) !== null) {
      const [d, mo, y] = m[1].split('/');
      dates.push(new Date(+y, +mo - 1, +d));
    }

    const name = extractName(line, tm.index);
    if (name) sections[cur].push({ name, time: fmtTime(tm[1]) });
  }

  const ORDER = ['ATÉ 75KG', 'DE 75KG A 90KG', 'ACIMA 90KG'];
  const categories = ORDER
    .filter(k => sections[k]?.length)
    .map(label => ({
      label,
      entries: sections[label].slice(0, 10).map((e, i) => ({
        pos:  i + 1,
        name: e.name,
        time: e.time,
      })),
    }));

  const periodStart = dates.length ? new Date(Math.min(...dates)).toLocaleDateString('pt-BR') : '';
  const periodEnd   = dates.length ? new Date(Math.max(...dates)).toLocaleDateString('pt-BR') : '';

  return { categories, periodStart, periodEnd };
}

/**
 * parsePDF(file) → Promise<{ categories, periodStart, periodEnd }>
 *
 * Usa pdf.js para extrair texto client-side.
 * Requer que pdfjsLib esteja disponível globalmente ou como import.
 */
async function parsePDF(file) {
  // Carrega pdf.js dinamicamente
  let pdfjsLib;
  try {
    pdfjsLib = (await import('pdfjs-dist')).default ?? await import('pdfjs-dist');
    // Worker CDN com versão dinâmica — evita mismatch entre pacote e worker
    if (!pdfjsLib.GlobalWorkerOptions?.workerSrc) {
      pdfjsLib.GlobalWorkerOptions.workerSrc =
        `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
    }
  } catch {
    throw new Error(
      'pdf.js não encontrado. Instale com: npm install pdfjs-dist\n' +
      'Ou use o parser Python (generate_ranking.py) para gerar os dados.'
    );
  }

  const buffer    = await file.arrayBuffer();
  const pdf       = await pdfjsLib.getDocument({ data: buffer }).promise;
  const lines     = [];

  for (let i = 1; i <= pdf.numPages; i++) {
    const page    = await pdf.getPage(i);
    const content = await page.getTextContent();
    const raw  = content.items.map(item => item.str).join(' ');
    // Normaliza tokens de tempo fragmentados pelo PDF:
    // "00:31 :21 2" → "00:31:212"  (join com espaço separa colon e dígitos)
    const text = raw
      .replace(/(\d)\s+:/g, '$1:')                          // "31 :" → "31:"
      .replace(/:\s*(\d+)\s+(\d+)/g, (_, a, b) => `:${a}${b}`); // ":21 2" → ":212"
    lines.push(...text.split(/\n|\s{3,}/));
  }

  return parseLines(lines);
}

// ─── Componente de upload de PDF ──────────────────────────────────────────────

function PDFUploader({ onParsed, trackKey }) {
  const [status,   setStatus]   = useState('idle'); // idle | loading | done | error
  const [message,  setMessage]  = useState('');
  const inputRef = useRef(null);

  const handleFile = useCallback(async (file) => {
    if (!file || !file.type.includes('pdf')) {
      setStatus('error');
      setMessage('Selecione um arquivo PDF válido.');
      return;
    }
    setStatus('loading');
    setMessage('Processando PDF...');
    try {
      const result = await parsePDF(file);
      if (!result.categories.length) {
        setStatus('error');
        setMessage('Nenhuma categoria encontrada. Verifique se o PDF é o relatório correto do Meta Kart.');
        return;
      }
      setStatus('done');
      setMessage(`${result.categories.length} categoria(s) extraída(s) com sucesso.`);
      onParsed(result);
    } catch (e) {
      setStatus('error');
      setMessage(String(e));
    }
  }, [onParsed]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files?.[0]);
  }, [handleFile]);

  const statusColors = {
    idle:    'rgba(255,255,255,0.15)',
    loading: '#6C34C8',
    done:    '#169630',
    error:   '#c83434',
  };

  return (
    <div
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border:       `2px dashed ${statusColors[status]}`,
        borderRadius: 8,
        padding:      '20px 16px',
        textAlign:    'center',
        cursor:       'pointer',
        transition:   'border-color 0.2s',
        background:   status === 'loading' ? 'rgba(108,52,200,0.08)' : 'transparent',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={e => handleFile(e.target.files?.[0])}
      />
      <div style={{ fontSize: 28, marginBottom: 8 }}>
        {status === 'loading' ? '⏳' : status === 'done' ? '✓' : status === 'error' ? '✗' : '📄'}
      </div>
      <div style={{
        color:      status === 'idle' ? 'rgba(255,255,255,0.5)' : '#fff',
        fontSize:   13,
        fontFamily: "'Montserrat', sans-serif",
      }}>
        {status === 'idle'
          ? `Arraste o PDF da ${trackKey.toUpperCase()} aqui ou clique para selecionar`
          : message}
      </div>
    </div>
  );
}

// ─── App Principal ────────────────────────────────────────────────────────────

const TRACK_LABELS = {
  barra:        'Barra (Roxo)',
  norte:        'Norte (Verde)',
  campo_grande: 'Campo Grande (Laranja)',
};
const TRACK_COLORS = {
  barra:        '#6C34C8',
  norte:        '#169630',
  campo_grande: '#FD8330',
};

export default function MetaKartApp() {
  const [track,    setTrack]    = useState('barra');
  const [format,   setFormat]   = useState('instagram');
  const [category, setCategory] = useState('ATÉ 75KG');
  const [period,   setPeriod]   = useState('');
  const [entries,  setEntries]  = useState(DEMO_ENTRIES);
  const [logoUrl,  setLogoUrl]  = useState(null);
  const [usePDF,   setUsePDF]   = useState(true);

  // Dados parseados do PDF, por pista
  const [pdfData, setPdfData] = useState({});

  const accentColor = TRACK_COLORS[track];

  // Quando o PDF for parseado, atualiza os dados da pista
  const handlePDFParsed = useCallback((result) => {
    setPdfData(prev => ({ ...prev, [track]: result }));

    // Seleciona a primeira categoria disponível
    if (result.categories.length) {
      const first = result.categories[0];
      setCategory(first.label);
      setEntries(first.entries);
    }
    if (result.periodStart && result.periodEnd) {
      setPeriod(`${result.periodStart} a ${result.periodEnd}`);
    }
  }, [track]);

  // Atualiza as entradas quando trocar de categoria (dados do PDF)
  useEffect(() => {
    if (!usePDF) return;
    const data = pdfData[track];
    if (!data) return;
    const cat = data.categories.find(c => c.label === category);
    if (cat) setEntries(cat.entries);
  }, [track, category, pdfData, usePDF]);

  const handleLogoUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setLogoUrl(ev.target.result);
    reader.readAsDataURL(file);
  };

  const updateEntry = (pos, field, value) => {
    setEntries(prev =>
      prev.map(e => e.pos === pos ? { ...e, [field]: field === 'name' ? value.toUpperCase() : value } : e)
    );
  };

  // Obtém categorias disponíveis (do PDF ou padrão)
  const availableCategories = usePDF && pdfData[track]
    ? pdfData[track].categories.map(c => c.label)
    : ['ATÉ 75KG', 'DE 75KG A 90KG', 'ACIMA 90KG'];

  // ─── Estilos ────────────────────────────────────────────────────────────────

  const selectStyle = {
    padding:      '9px 12px',
    background:   '#1a1a30',
    border:       `1px solid rgba(255,255,255,0.12)`,
    borderRadius: 6,
    color:        '#fff',
    fontFamily:   "'Montserrat', sans-serif",
    fontSize:     13,
    cursor:       'pointer',
    width:        '100%',
    outline:      'none',
  };
  const labelStyle = {
    display:       'block',
    color:         'rgba(255,255,255,0.5)',
    fontSize:      11,
    letterSpacing: '0.1em',
    marginBottom:  6,
    fontFamily:    "'Montserrat', sans-serif",
    fontWeight:    600,
  };
  const inputStyle = { ...selectStyle };

  return (
    <div style={{
      minHeight:     '100vh',
      background:    '#080814',
      padding:       '20px 16px 40px',
      display:       'flex',
      flexDirection: 'column',
      gap:           20,
      fontFamily:    "'Montserrat', sans-serif",
    }}>
      {/* Carrega as fontes */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;600;700&display=swap');
        *, *::before, *::after { box-sizing: border-box; }
        select option { background: #1a1a30; }
        input[type=range] { accent-color: ${accentColor}; }
        ::-webkit-scrollbar { width: 6px; background: #12122a; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
      `}</style>

      {/* Header */}
      <div style={{
        display:    'flex',
        alignItems: 'center',
        gap:        12,
        paddingBottom: 16,
        borderBottom: '1px solid rgba(255,255,255,0.07)',
      }}>
        <div style={{
          width:        4,
          height:       36,
          background:   accentColor,
          borderRadius: 2,
          transition:   'background 0.3s',
        }} />
        <div>
          <div style={{
            fontFamily:    "'Bebas Neue', sans-serif",
            fontSize:      24,
            color:         '#fff',
            letterSpacing: '0.06em',
            lineHeight:    1,
          }}>
            META KART — GERADOR DE RANKING
          </div>
          <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 12, marginTop: 2 }}>
            Indoor Karting · Cards para Instagram e TV
          </div>
        </div>
      </div>

      {/* Corpo principal */}
      <div style={{
        display:    'flex',
        gap:        20,
        alignItems: 'flex-start',
        flexWrap:   'wrap',
      }}>
        {/* ── Coluna de controles ──────────────────────────────────────────── */}
        <div style={{
          width:         300,
          flexShrink:    0,
          display:       'flex',
          flexDirection: 'column',
          gap:           16,
          background:    '#10102a',
          padding:       18,
          borderRadius:  10,
          border:        '1px solid rgba(255,255,255,0.07)',
        }}>
          {/* Seletor de pista */}
          <div>
            <label style={labelStyle}>PISTA</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {Object.entries(TRACK_LABELS).map(([key, lbl]) => (
                <button
                  key={key}
                  onClick={() => setTrack(key)}
                  style={{
                    flex:         1,
                    padding:      '8px 4px',
                    borderRadius: 6,
                    border:       track === key
                      ? `2px solid ${TRACK_COLORS[key]}`
                      : '2px solid rgba(255,255,255,0.08)',
                    background:   track === key
                      ? `${TRACK_COLORS[key]}22`
                      : 'transparent',
                    color:        track === key ? '#fff' : 'rgba(255,255,255,0.4)',
                    cursor:       'pointer',
                    fontSize:     10,
                    fontWeight:   700,
                    letterSpacing: '0.06em',
                    transition:   'all 0.15s',
                  }}
                >
                  {key === 'campo_grande' ? 'C.GRANDE' : key.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Formato */}
          <div>
            <label style={labelStyle}>FORMATO DE SAÍDA</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {[
                { value: 'instagram', label: 'Instagram\n1080×1350' },
                { value: 'tv',        label: 'TV Wide\n1920×1080'  },
              ].map(f => (
                <button
                  key={f.value}
                  onClick={() => setFormat(f.value)}
                  style={{
                    flex:         1,
                    padding:      '8px 4px',
                    borderRadius: 6,
                    border:       format === f.value
                      ? `2px solid ${accentColor}`
                      : '2px solid rgba(255,255,255,0.08)',
                    background:   format === f.value ? `${accentColor}22` : 'transparent',
                    color:        format === f.value ? '#fff' : 'rgba(255,255,255,0.4)',
                    cursor:       'pointer',
                    fontSize:     10,
                    fontWeight:   700,
                    letterSpacing: '0.04em',
                    whiteSpace:   'pre-line',
                    lineHeight:   1.4,
                    transition:   'all 0.15s',
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Categoria */}
          <div>
            <label style={labelStyle}>CATEGORIA</label>
            <select
              value={category}
              onChange={e => setCategory(e.target.value)}
              style={selectStyle}
            >
              {availableCategories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Período */}
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

          {/* Logo */}
          <div>
            <label style={labelStyle}>LOGO META KART (PNG transparente)</label>
            <input
              type="file"
              accept="image/png,image/webp,image/svg+xml"
              onChange={handleLogoUpload}
              style={{ ...inputStyle, padding: '7px 8px', fontSize: 11 }}
            />
            {logoUrl && (
              <div style={{
                marginTop:    8,
                padding:      '6px 10px',
                background:   'rgba(255,255,255,0.04)',
                borderRadius: 4,
                display:      'flex',
                alignItems:   'center',
                gap:          10,
              }}>
                <img src={logoUrl} alt="logo" style={{
                  maxWidth: 70, maxHeight: 28,
                  filter:   'brightness(0) invert(1)',
                }} />
                <span style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11 }}>
                  Carregada
                </span>
              </div>
            )}
          </div>

          {/* Toggle: PDF upload ou manual */}
          <div style={{
            display:      'flex',
            alignItems:   'center',
            gap:          10,
            padding:      '10px 0',
            borderTop:    '1px solid rgba(255,255,255,0.06)',
            borderBottom: '1px solid rgba(255,255,255,0.06)',
          }}>
            <span style={{ ...labelStyle, margin: 0, flex: 1 }}>DADOS VIA UPLOAD PDF</span>
            <button
              onClick={() => setUsePDF(v => !v)}
              style={{
                width:        40,
                height:       22,
                borderRadius: 11,
                border:       'none',
                background:   usePDF ? accentColor : 'rgba(255,255,255,0.15)',
                cursor:       'pointer',
                position:     'relative',
                transition:   'background 0.2s',
              }}
            >
              <div style={{
                position:     'absolute',
                top:          3,
                left:         usePDF ? 21 : 3,
                width:        16,
                height:       16,
                borderRadius: '50%',
                background:   '#fff',
                transition:   'left 0.2s',
              }} />
            </button>
          </div>

          {/* PDF Uploader */}
          {usePDF && (
            <PDFUploader
              onParsed={handlePDFParsed}
              trackKey={track}
            />
          )}

          {/* Editor manual de pilotos */}
          {!usePDF && (
            <div>
              <label style={{ ...labelStyle, marginBottom: 10 }}>PILOTOS (EDIÇÃO MANUAL)</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                {entries.map(e => (
                  <div key={e.pos} style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
                    <span style={{
                      fontFamily: "'Bebas Neue', sans-serif",
                      fontSize:   16,
                      color:      e.pos === 1 ? '#D4AF37'
                                : e.pos === 2 ? '#A8A9AD'
                                : e.pos === 3 ? '#CD7F32'
                                : 'rgba(255,255,255,0.3)',
                      width:      20,
                      textAlign:  'center',
                      flexShrink: 0,
                    }}>
                      {e.pos}
                    </span>
                    <input
                      value={e.name}
                      onChange={ev => updateEntry(e.pos, 'name', ev.target.value)}
                      style={{ ...inputStyle, flex: 1, fontSize: 11, padding: '5px 8px' }}
                    />
                    <input
                      value={e.time}
                      onChange={ev => updateEntry(e.pos, 'time', ev.target.value)}
                      style={{
                        ...inputStyle,
                        width:      68,
                        fontSize:   11,
                        padding:    '5px 6px',
                        fontFamily: 'monospace',
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Preview do card ──────────────────────────────────────────────── */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <MetaKartRankingCard
            track={track}
            format={format}
            category={category}
            period={period}
            entries={entries}
            logoUrl={logoUrl}
          />

          {/* Dica de exportação */}
          <div style={{
            marginTop:  12,
            padding:    '10px 14px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 6,
            border:     '1px solid rgba(255,255,255,0.06)',
            color:      'rgba(255,255,255,0.35)',
            fontSize:   12,
            lineHeight: 1.6,
          }}>
            <strong style={{ color: 'rgba(255,255,255,0.6)' }}>Dica de export:</strong>{' '}
            O PNG exportado terá a resolução completa (1080×1350 ou 1920×1080) independentemente
            do zoom do browser. As fontes devem estar carregadas antes de exportar — aguarde
            o carregamento inicial da página.
          </div>
        </div>
      </div>
    </div>
  );
}
