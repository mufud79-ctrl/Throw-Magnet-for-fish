// node model_views.mjs <model.glb> <out.jpg> [yaw[:pitch],...] [--wide]   -> a contact sheet of turntable views
// --wide: 1280x540 landscape frames (long models: serpents, weapons); yaw:pitch[:zoom[:fz]] e.g. 0:90 top view; 30:15:4:0.8 = 4x zoom on the +Z end
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const argv = process.argv.slice(2); const wide = argv.includes('--wide'); const [glb, out, yaws = '0,90,180,270'] = argv.filter((a) => a !== '--wide');
const [VW, VH] = wide ? [1280, 540] : [640, 900];
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: VW, height: VH } });
page.on('pageerror', (e) => console.error('pageerror', e.message));
await page.route('http://lab.local/**', (r) => {
  const p = decodeURIComponent(new URL(r.request().url()).pathname);
  const f = p === '/model.glb' ? path.resolve(glb) : p.startsWith('/three/') ? path.join(here, 'node_modules', p) : path.join(here, p);
  if (!fs.existsSync(f)) return r.fulfill({ status: 404 });
  r.fulfill({ path: f, contentType: f.endsWith('.js') ? 'application/javascript' : f.endsWith('.html') ? 'text/html' : 'application/octet-stream' });
});
await page.goto('http://lab.local/page/model.html'); await page.waitForFunction(() => window.MODEL_READY);
const size = await page.evaluate(() => window.MODEL.load('/model.glb'));
console.log('size', size.map((v) => v.toFixed(2)).join(' x '));
const tmp = fs.mkdtempSync('/tmp/mv_'); const ys = yaws.split(',').map((v) => v.split(':').map(Number));
for (const [i, y] of ys.entries()) { const u = await page.evaluate((y) => window.MODEL.view(y[0], y.length > 1 ? y[1] : 4, y[2] || 1, y[3] || 0), y); fs.writeFileSync(path.join(tmp, `v${i}.jpg`), Buffer.from(u.split(',')[1], 'base64')); }
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(tmp, 'v%d.jpg'), '-vf', wide ? `scale=960:-1,tile=2x${Math.ceil(ys.length / 2)}` : `scale=480:-1,tile=${ys.length}x1`, '-frames:v', '1', out]);
await browser.close(); console.log(out);
