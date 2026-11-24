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
  blue: { glow: '#2f5bff', rim: '#0b1a6e', mid: '#7aa2ff', core: '#ffffff', bg: '#0d1530' },
  ink: { glow: '#2f5bff', rim: '#ffffff', mid: '#0a1a6a', core: '#ffffff', bg: '#0d1530' },
  dark: { glow: '#8090a0', rim: '#08080c', mid: '#6a6e78', core: '#ffffff', bg: '#3a4050' },
  fire: { glow: '#ff6a10', rim: '#c02008', mid: '#ff9a20', core: '#fff6d0', bg: '#202028' },
  wind: { glow: '#a0b0c0', rim: '#505868', mid: '#d0d8e0', core: '#ffffff', bg: '#3a4050' },
};
const palFor = (d) => ({ saw_fan: PAL.ink, star4: PAL.ink, ring_slash: PAL.dark, fire_burst: PAL.fire, trail_arc: PAL.wind }[d] || PAL.blue);
const board = [];
for (const def of want) {
  const t0 = Date.now();
  const res = await page.evaluate(({ def, pal }) => {
    const o = VFXPaint.build(def), files = {};
    for (const [k, c] of Object.entries(o)) files[k] = c.toDataURL('image/png');
    const S = 1024, c = document.createElement('canvas'); c.width = c.height = S;
    const g = c.getContext('2d'); g.fillStyle = pal.bg; g.fillRect(0, 0, S, S);
    if (VFXPaint.layered(def)) {
      for (const L of ['glow', 'rim', 'mid', 'core']) {
        const src = o[`${def}_${L}`], t = document.createElement('canvas'); t.width = t.height = S;
        const tg = t.getContext('2d'); tg.drawImage(src, 0, 0, S, S); tg.globalCompositeOperation = 'source-in'; tg.fillStyle = pal[L]; tg.fillRect(0, 0, S, S);
        g.globalAlpha = L === 'glow' ? 0.9 : 1; g.globalCompositeOperation = L === 'glow' || L === 'core' ? 'lighter' : 'source-over'; g.drawImage(t, 0, 0);
      }
    } else g.drawImage(o[def], 0, 0, S, S);
    return { files, preview: c.toDataURL('image/png') };
  }, { def, pal: palFor(def) });
  for (const [k, u] of Object.entries(res.files)) fs.writeFileSync(path.join(out, k + '.png'), Buffer.from(u.split(',')[1], 'base64'));
  fs.writeFileSync(path.join(out, `_preview_${def}.png`), Buffer.from(res.preview.split(',')[1], 'base64'));
  board.push(def);
  console.log(def, Object.keys(res.files).length, 'file(s)', Date.now() - t0 + 'ms');
}
await browser.close();
