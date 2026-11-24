// Headless paint: node paint.mjs [def ...]  -> out/textures/<tex>.png (white layers) + out/textures/_preview_<def>.png
// The preview tints each layer (glow/rim/mid/core) with a test palette so the stacked result can be reviewed.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const out = path.join(here, 'out', 'textures');
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
await page.setContent('<!doctype html><body></body>');
await page.addScriptTag({ content: fs.readFileSync(path.join(here, 'engine/paint.js'), 'utf8') });
const all = await page.evaluate(() => Object.keys(VFXPaint.defs));
const want = process.argv.slice(2).length ? process.argv.slice(2) : all;
const PAL = {
  fire: { glow: '#ff6a1a', rim: '#7a0c06', mid: '#ff7a14', core: '#fff3c4' },
  smoke: { glow: '#3a3040', rim: '#1c1620', mid: '#5c5068', core: '#9a8aa0' },
  steel: { glow: '#3aa0ff', rim: '#123a9c', mid: '#8fdcff', core: '#ffffff' },
};
const palFor = (d) => (d.includes('smoke') ? PAL.smoke : d.includes('slash') && !d.includes('fire') ? PAL.steel : PAL.fire);
for (const def of want) {
  const t0 = Date.now();
  const res = await page.evaluate(({ def, pal }) => {
    const o = VFXPaint.build(def), files = {};
    for (const [k, c] of Object.entries(o)) files[k] = c.toDataURL('image/png');
    let preview = null;
    if (VFXPaint.defs[def].layered) {
      const S = 1024, c = document.createElement('canvas'); c.width = c.height = S;
      const g = c.getContext('2d'); g.fillStyle = '#2a2633'; g.fillRect(0, 0, S, S);
      for (const L of ['glow', 'rim', 'mid', 'core']) {
        const src = o[`${def}_${L}`], t = document.createElement('canvas'); t.width = t.height = S;
        const tg = t.getContext('2d'); tg.drawImage(src, 0, 0); tg.globalCompositeOperation = 'source-in'; tg.fillStyle = pal[L]; tg.fillRect(0, 0, S, S);
        g.globalAlpha = L === 'glow' ? 0.45 : 1; g.globalCompositeOperation = L === 'glow' ? 'lighter' : 'source-over'; g.drawImage(t, 0, 0);
      }
      preview = c.toDataURL('image/png');
    }
    return { files, preview };
  }, { def, pal: palFor(def) });
  for (const [k, u] of Object.entries(res.files)) fs.writeFileSync(path.join(out, k + '.png'), Buffer.from(u.split(',')[1], 'base64'));
  if (res.preview) fs.writeFileSync(path.join(out, `_preview_${def}.png`), Buffer.from(res.preview.split(',')[1], 'base64'));
  console.log(def, Object.keys(res.files).length, 'file(s)', Date.now() - t0 + 'ms');
}
await browser.close();
