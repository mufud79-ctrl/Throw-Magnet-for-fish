// node model_views.mjs <model.glb> <out.jpg> [yaw,yaw,...] [WxH]   -> a contact sheet of turntable views (default 640x900)
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const [glb, out, yaws = '0,90,180,270', vp = '640x900'] = process.argv.slice(2);
const [VW, VH] = vp.split('x').map(Number);
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 640, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror', e.message));
await page.route('http://lab.local/**', (r) => {
  const p = decodeURIComponent(new URL(r.request().url()).pathname);
  const f = p === '/model.glb' ? path.resolve(glb) : p.startsWith('/three/') ? path.join(here, 'node_modules', p) : path.join(here, p);
  if (!fs.existsSync(f)) return r.fulfill({ status: 404 });
  r.fulfill({ path: f, contentType: f.endsWith('.js') ? 'application/javascript' : f.endsWith('.html') ? 'text/html' : 'application/octet-stream' });
});
await page.goto('http://lab.local/page/model.html'); await page.waitForFunction(() => window.MODEL_READY);
await page.evaluate(([w, h]) => window.MODEL.resize(w, h), [VW, VH]);
const size = await page.evaluate(() => window.MODEL.load('/model.glb'));
console.log('size', size.map((v) => v.toFixed(2)).join(' x '));
const tmp = fs.mkdtempSync('/tmp/mv_'); const ys = yaws.split(',').map(Number);
for (const [i, y] of ys.entries()) { const u = await page.evaluate((y) => window.MODEL.view(y), y); fs.writeFileSync(path.join(tmp, `v${i}.jpg`), Buffer.from(u.split(',')[1], 'base64')); }
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(tmp, 'v%d.jpg'), '-vf', `scale=${Math.round(480 * VW / 640)}:-1,tile=${ys.length}x1`, '-frames:v', '1', out]);
await browser.close(); console.log(out);
