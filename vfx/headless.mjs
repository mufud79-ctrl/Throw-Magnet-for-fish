// Headless "Studio": render out/lab.html in Chromium.
//   node headless.mjs <Effect> sheet [t1,t2,...] [env] [camX:camY:camZ]  -> out/<Effect>/sheet.png
//   node headless.mjs <Effect> shot [t]                                   -> out/<Effect>/page.png (full page)
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const [name = 'AzureTempest', mode = 'sheet', times, env, cam] = process.argv.slice(2);
const dir = path.join(here, 'out', name);
fs.mkdirSync(dir, { recursive: true });
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
  + fs.readFileSync(path.join(here, 'out', 'lab.html'), 'utf8') + '</body></html>';
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
await page.route('https://cdn.jsdelivr.net/npm/three@0.147.0/**', (r) => {
  const p = new URL(r.request().url()).pathname.replace('/npm/three@0.147.0/', '');
  r.fulfill({ path: path.join(here, 'node_modules/three', p), contentType: 'application/javascript' });
});
await page.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ body: '', contentType: 'text/css' }));
await page.addInitScript(() => { window.VFX_HEADLESS = true; });
await page.setContent(html, { waitUntil: 'load' });
await page.waitForFunction(() => window.VFX, null, { timeout: 60000 });
await page.evaluate(async (n) => { await VFX.ready; await VFX.load(n); }, name);
if (errors.length) console.error('PAGE ERRORS:\n' + errors.join('\n'));
const dur = await page.evaluate(() => VFX.sim.fx.duration);
const ts = times ? times.split(',').map(Number) : Array.from({ length: 12 }, (_, i) => +((0.05 + (i / 11) * (dur - 0.15)).toFixed(2)));
if (mode === 'frames') {
  const shots = await page.evaluate(({ ts, env }) => { if (env) VFX.setEnv(env); const src = document.querySelector('#vp'); return ts.map((t) => { VFX.frame(t); return src.toDataURL('image/png'); }); }, { ts, env });
  shots.forEach((u, k) => fs.writeFileSync(path.join(dir, `f_${ts[k].toFixed(2)}.png`), Buffer.from(u.split(',')[1], 'base64')));
  console.log('frames', shots.length);
} else if (mode === 'shot') {
  await page.evaluate((t) => VFX.frame(t), ts[0]);
  await page.screenshot({ path: path.join(dir, 'page.png') });
  console.log(path.join(dir, 'page.png'));
} else {
  const data = await page.evaluate(({ ts, env, cam }) => {
    if (env) VFX.setEnv(env);
    const src = document.querySelector('#vp'), shots = [];
    for (const t of ts) {
      if (cam) { const c = cam.split(':').map(Number); VFX.camera.position.set(c[0], c[1], c[2]); }
      VFX.frame(t); shots.push(src.toDataURL('image/png'));
    }
    return { shots, w: src.width, h: src.height };
  }, { ts, env, cam });
  const out = await page.evaluate(async ({ shots, w, h, ts }) => {
    const cols = Math.min(4, shots.length), rows = Math.ceil(shots.length / cols), sw = 480, sh = Math.round(480 * h / w);
    const c = document.createElement('canvas'); c.width = cols * sw; c.height = rows * sh;
    const g = c.getContext('2d');
    for (let i = 0; i < shots.length; i++) {
      const im = new Image(); im.src = shots[i]; await im.decode();
      const x = (i % cols) * sw, y = Math.floor(i / cols) * sh;
      g.drawImage(im, x, y, sw, sh);
      g.fillStyle = '#000a'; g.fillRect(x, y, 70, 22); g.fillStyle = '#ffa51e'; g.font = '14px monospace'; g.fillText(ts[i].toFixed(2) + 's', x + 6, y + 16);
    }
    return c.toDataURL('image/png');
  }, { ...data, ts });
  fs.writeFileSync(path.join(dir, 'sheet.png'), Buffer.from(out.split(',')[1], 'base64'));
  console.log(path.join(dir, 'sheet.png'));
}
await browser.close();
