// Headless renderer: plays effect JSON in page/vfx.js (three.js emulator) and writes video + contact sheet.
//   node render.mjs <effect.json | dir> [...] [--out DIR] [--fps 30]
// Per effect: OUT/<name>.mp4 (H.264, 640x360), OUT/<name>_sheet.jpg (8 frames), OUT/<name>_poster.jpg
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const assets = path.join(here, '..', 'assets');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const out = opt('--out', path.join(here, 'out')), fps = +opt('--fps', 30);
fs.mkdirSync(out, { recursive: true });
let files = [];
for (const a of args) files = files.concat(fs.statSync(a).isDirectory() ? fs.readdirSync(a).filter((f) => f.endsWith('.json')).sort().map((f) => path.join(a, f)) : [a]);
const types = { '.js': 'application/javascript', '.html': 'text/html', '.png': 'image/png', '.json': 'application/json' };
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
await page.route('http://lab.local/**', (r) => {
  const p = decodeURIComponent(new URL(r.request().url()).pathname);
  let f = null;
  if (p.startsWith('/three/')) f = path.join(here, 'node_modules', p);
  else if (p.startsWith('/assets/')) f = path.join(assets, p.slice(8));
  else if (p.startsWith('/page/')) f = path.join(here, p);
  if (!f || !fs.existsSync(f)) return r.fulfill({ status: 404, body: 'nf ' + p });
  r.fulfill({ path: f, contentType: types[path.extname(f)] || 'application/octet-stream' });
});
await page.goto('http://lab.local/page/index.html');
await page.waitForFunction(() => window.LAB_READY, null, { timeout: 60000 });
if (process.env.NOPOST) await page.evaluate((v) => { window.LAB_NOPOST = v; }, +process.env.NOPOST);
for (const f of files) {
  const fx = JSON.parse(fs.readFileSync(f, 'utf8'));
  const name = fx.name, tmp = path.join(out, '_f_' + name);
  fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp);
  const t0 = Date.now();
  const dur = await page.evaluate((fx) => window.LAB.load(fx, '/assets'), fx);
  const n = Math.round(dur * fps);
  for (let i = 0; i < n; i++) {
    const url = await page.evaluate((t) => window.LAB.frame(t), i / fps);
    fs.writeFileSync(path.join(tmp, `f_${String(i).padStart(4, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
  }
  const ff = (a) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...a]);
  ff(['-framerate', String(fps), '-i', path.join(tmp, 'f_%04d.jpg'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', path.join(out, name + '.mp4')]);
  const step = Math.max(1, Math.floor(n / 8));
  ff(['-i', path.join(tmp, 'f_%04d.jpg'), '-vf', `select='not(mod(n\\,${step}))',scale=320:-1,tile=4x2`, '-frames:v', '1', path.join(out, name + '_sheet.jpg')]);
  const peak = fx.poster !== undefined ? Math.min(n - 1, Math.round(fx.poster * fps)) : Math.floor(n * 0.3);
  fs.copyFileSync(path.join(tmp, `f_${String(peak).padStart(4, '0')}.jpg`), path.join(out, name + '_poster.jpg'));
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`${name}: ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s${errors.length ? '  ERR ' + errors.splice(0).join(' | ') : ''}`);
}
await browser.close();
