// Headless "Studio": render the built page in Chromium, then
//   node headless.mjs <Name> sheet [t1,t2,...] [env] [camX,camY,camZ]  -> out/<Name>/sheet.png (contact sheet)
//   node headless.mjs <Name> export                                     -> out/<Name>/textures/*.png + <Name>.lua
//   node headless.mjs <Name> textures                                   -> out/<Name>/texture_sheet.png
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const [name = 'FireExplosion', mode = 'sheet', times, env = 'dusk', cam] = process.argv.slice(2);
const dir = path.join(here, 'out', name);
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
  + fs.readFileSync(path.join(dir, name + '.html'), 'utf8') + '</body></html>';
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 860 }, deviceScaleFactor: 1 });
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
if (errors.length) console.error('PAGE ERRORS:\n' + errors.join('\n'));

if (mode === 'sheet' || mode === 'shot') {
  const ts = (times || '0.1,0.25,0.31,0.35,0.4,0.45,0.55,0.7,0.9,1.2,1.6,2.1').split(',').map(Number);
  const data = await page.evaluate(({ ts, env, cam }) => {
    VFX.setEnv(env);
    if (cam) { const c = cam.split(':').map(Number); VFX.camera.position.set(c[0], c[1], c[2]); }
    const src = document.querySelector('#vp'), shots = [];
    for (const t of ts) { VFX.frame(t); shots.push(src.toDataURL('image/png')); }
    return { shots, w: src.width, h: src.height };
  }, { ts, env, cam });
  const out = await page.evaluate(async ({ shots, w, h, ts }) => {
    const cols = Math.min(4, shots.length), rows = Math.ceil(shots.length / cols), sw = 480, sh = Math.round(480 * h / w);
    const c = document.createElement('canvas'); c.width = cols * sw; c.height = rows * sh;
    const g = c.getContext('2d');
    for (let i = 0; i < shots.length; i++) {
      const im = new Image(); im.src = shots[i]; await im.decode();
      g.drawImage(im, (i % cols) * sw, Math.floor(i / cols) * sh, sw, sh);
      g.fillStyle = '#000a'; g.fillRect((i % cols) * sw, Math.floor(i / cols) * sh, 70, 22);
      g.fillStyle = '#ffa51e'; g.font = '14px monospace'; g.fillText(ts[i].toFixed(2) + 's', (i % cols) * sw + 6, Math.floor(i / cols) * sh + 16);
    }
    return c.toDataURL('image/png');
  }, { ...data, ts });
  const file = path.join(dir, mode === 'shot' ? 'shot.png' : 'sheet.png');
  fs.writeFileSync(file, Buffer.from(out.split(',')[1], 'base64'));
  if (mode === 'shot') await page.screenshot({ path: path.join(dir, 'page.png') });
  console.log(file);
} else if (mode === 'textures' || mode === 'export') {
  const res = await page.evaluate(() => {
    const names = [...new Set(VFX.sim.fx.layers.map((l) => l.props.Texture))];
    return { names, pngs: names.map((n) => VFX.texturePNG(n)), luau: VFX.luau };
  });
  if (mode === 'export') {
    fs.mkdirSync(path.join(dir, 'textures'), { recursive: true });
    res.names.forEach((n, i) => fs.writeFileSync(path.join(dir, 'textures', n + '.png'), Buffer.from(res.pngs[i].split(',')[1], 'base64')));
    fs.writeFileSync(path.join(dir, name + '.lua'), res.luau);
    console.log('exported', res.names.length, 'textures +', name + '.lua');
  } else {
    const out = await page.evaluate(async ({ pngs, names }) => {
      const S = 300, cols = 4, c = document.createElement('canvas'); c.width = cols * S; c.height = Math.ceil(pngs.length / cols) * (S + 20);
      const g = c.getContext('2d'); g.fillStyle = '#2a2633'; g.fillRect(0, 0, c.width, c.height);
      for (let i = 0; i < pngs.length; i++) {
        const im = new Image(); im.src = pngs[i]; await im.decode();
        const x = (i % cols) * S, y = Math.floor(i / cols) * (S + 20);
        g.drawImage(im, x + 4, y + 4, S - 8, S - 8); g.fillStyle = '#fff'; g.font = '13px monospace'; g.fillText(names[i], x + 6, y + S + 12);
      }
      return c.toDataURL('image/png');
    }, res);
    fs.writeFileSync(path.join(dir, 'texture_sheet.png'), Buffer.from(out.split(',')[1], 'base64'));
    console.log(path.join(dir, 'texture_sheet.png'));
  }
}
await browser.close();
