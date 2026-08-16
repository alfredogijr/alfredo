// Gera os PNGs das artes em out/. Uso: node src/render.mjs
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, '..', 'out');
const CREME = '#FAF6EE', PRETO = '#0B0B0B', MOSTARDA = '#E3A81C';

// Formatos de feed: 4:5 é o padrão do Instagram hoje (ocupa mais tela).
const FORMATOS = [
  { pasta: '4x5', w: 1080, h: 1350 },
  { pasta: '1x1', w: 1080, h: 1080 },
];

const feed = [
  { nome: '01-wordmark',    bg: CREME, fg: PRETO,
    lines: ['grão de mostarda'], r: 'arco', fill: 0.80 },
  { nome: '02-espelhado',   bg: CREME, fg: PRETO,
    lines: ['grão de mostarda'], r: 'espelhado', fill: 0.80 },
  { nome: '03-duas-linhas', bg: CREME, fg: PRETO,
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.72 },
  { nome: '04-mostarda',    bg: MOSTARDA, fg: '#141210',
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.72 },
  { nome: '05-slide2',      bg: CREME, fg: PRETO,
    lines: ['instagram novo,', 'grão de mostarda', 'de sempre.'], r: 'arco', fill: 0.70 },
];

const artes = [
  ...FORMATOS.flatMap(f => feed.map(a =>
    ({ ...a, w: f.w, h: f.h, arquivo: path.join(f.pasta, a.nome + '.png') }))),
  { nome: 'story', w: 1080, h: 1920, bg: CREME, fg: PRETO, arquivo: 'story.png',
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.78 },
];

const browser = await chromium.launch();
for (const arte of artes) {
  const destino = path.join(out, arte.arquivo);
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  const page = await browser.newPage({
    viewport: { width: arte.w, height: arte.h }, deviceScaleFactor: 1 });
  const url = 'file://' + path.join(dir, 'page.html')
            + '?cfg=' + encodeURIComponent(JSON.stringify(arte));
  await page.goto(url);
  await page.waitForFunction(() => document.title === 'pronto');
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: destino });
  await page.close();
  console.log('✓', arte.arquivo, arte.w + 'x' + arte.h);
}
await browser.close();
