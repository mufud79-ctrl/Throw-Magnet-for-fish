// node turntable.mjs <model.glb>[,more.glb ...] <out.mp4> [--frames 96] [--pitch 12] [--wide] [--zoom 1]
// A 360-degree turntable MP4 of one or more GLBs (several are tiled side by side, each in its own cell).
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); if (i < 0) return d; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const frames = +opt('--frames', 96), pitch = +opt('--pitch', 12), zoom = +opt('--zoom', 1);
const wide = argv.includes('--wide'); const rest = argv.filter((a) => a !== '--wide');
const [glbs, out] = [rest[0].split(','), rest[1]];
const [VW, VH] = wide ? [1280, 540] : glbs.length > 1 ? [480, 540] : [720, 720];
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const tmp = fs.mkdtempSync('/tmp/tt_');
for (const [gi, glb] of glbs.entries()) {
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
  console.log(path.basename(glb), 'size', size.map((v) => v.toFixed(2)).join(' x '));
  for (let i = 0; i < frames; i++) {
    const u = await page.evaluate(([y, p, z]) => window.MODEL.view(y, p, z), [i * 360 / frames, pitch, zoom]);
    fs.writeFileSync(path.join(tmp, `g${gi}_${String(i).padStart(4, '0')}.jpg`), Buffer.from(u.split(',')[1], 'base64'));
  }
  await page.close();
}
await browser.close();
const inputs = glbs.flatMap((_, gi) => ['-framerate', '24', '-i', path.join(tmp, `g${gi}_%04d.jpg`)]);
const filter = glbs.length > 1 ? ['-filter_complex', `${glbs.map((_, i) => `[${i}:v]`).join('')}hstack=inputs=${glbs.length},scale=trunc(iw/2)*2:trunc(ih/2)*2`] : [];
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, ...filter, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out]);
console.log(out);
