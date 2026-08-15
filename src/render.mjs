// Gera os PNGs das artes em out/. Uso: node src/render.mjs
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const CREME = '#FAF6EE', PRETO = '#0B0B0B', MOSTARDA = '#E3A81C';

const artes = [
  { nome: '01-feed-wordmark',   w: 1080, h: 1080, bg: CREME, fg: PRETO,
    lines: ['grão de mostarda'], r: 'arco', fill: 0.80 },
  { nome: '02-feed-espelhado',  w: 1080, h: 1080, bg: CREME, fg: PRETO,
    lines: ['grão de mostarda'], r: 'espelhado', fill: 0.80 },
  { nome: '03-feed-duas-linhas', w: 1080, h: 1080, bg: CREME, fg: PRETO,
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.72 },
  { nome: '04-feed-mostarda',   w: 1080, h: 1080, bg: MOSTARDA, fg: '#141210',
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.72 },
  { nome: '05-feed-slide2',     w: 1080, h: 1080, bg: CREME, fg: PRETO,
    lines: ['instagram novo,', 'grão de mostarda', 'de sempre.'], r: 'arco', fill: 0.70 },
  { nome: '06-story',           w: 1080, h: 1920, bg: CREME, fg: PRETO,
    lines: ['grão de', 'mostarda'], r: 'arco', fill: 0.78 },
];

const browser = await chromium.launch();
for (const arte of artes) {
  const page = await browser.newPage({
    viewport: { width: arte.w, height: arte.h }, deviceScaleFactor: 1 });
  const url = 'file://' + path.join(dir, 'page.html')
            + '?cfg=' + encodeURIComponent(JSON.stringify(arte));
  await page.goto(url);
  await page.waitForFunction(() => document.title === 'pronto');
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(dir, '..', 'out', arte.nome + '.png') });
  await page.close();
  console.log('✓', arte.nome + '.png', arte.w + 'x' + arte.h);
}
await browser.close();
