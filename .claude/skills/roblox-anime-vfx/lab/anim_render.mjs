// node anim_render.mjs <anim.glb> <out_basename> [--fps 30] [--size 720x900] [--yaw 25] [--orbit 360] [--loops 1] [--period S]
//   --period: loop length when the clip's last key repeats its first (closed loops), so loops don't hitch
//   -> <out>.mp4 (H.264) and <out>.gif (palette, 15 fps, 480 px wide). --orbit spins the camera by that many
//   degrees over the whole render (loops x clip duration); otherwise the camera is fixed at --yaw.
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const fps = +opt('--fps', 30), size = opt('--size', '720x900'), yaw = +opt('--yaw', 25), orbit = +opt('--orbit', 0), loops = +opt('--loops', 1), pitch = +opt('--pitch', 6), zoom = +opt('--zoom', 1);
const period = +opt('--period', 0);
const [glb, out] = args; const [W, H] = size.split('x').map(Number);
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('pageerror', (e) => console.error('pageerror', e.message));
await page.route('http://lab.local/**', (r) => {
  const p = decodeURIComponent(new URL(r.request().url()).pathname);
  const f = p === '/model.glb' ? path.resolve(glb) : p.startsWith('/three/') ? path.join(here, 'node_modules', p) : path.join(here, p);
  if (!fs.existsSync(f)) return r.fulfill({ status: 404 });
  r.fulfill({ path: f, contentType: f.endsWith('.js') ? 'application/javascript' : f.endsWith('.html') ? 'text/html' : 'application/octet-stream' });
});
await page.goto('http://lab.local/page/anim.html'); await page.waitForFunction(() => window.ANIM_READY);
await page.evaluate(([w, h]) => window.ANIM.resize(w, h), [W, H]);
const info = await page.evaluate(() => window.ANIM.load('/model.glb'));
console.log('clips', JSON.stringify(info.clips));
const dur = period || info.clips.reduce((m, c) => Math.max(m, c[1]), 0);
const n = Math.round(dur * loops * fps);
const tmp = fs.mkdtempSync('/tmp/anim_');
for (let i = 0; i < n; i++) {
  const t = (i / fps) % dur, y = yaw + (orbit ? orbit * i / n : 0);
  const u = await page.evaluate(([t, y, p, z]) => window.ANIM.frame(t, y, p, z), [t, y, pitch, zoom]);
  fs.writeFileSync(path.join(tmp, `f${String(i).padStart(4, '0')}.jpg`), Buffer.from(u.split(',')[1], 'base64'));
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(tmp, 'f%04d.jpg'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out + '.mp4']);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', out + '.mp4', '-vf', 'fps=15,scale=420:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=sierra2_4a', out + '.gif']);
fs.rmSync(tmp, { recursive: true, force: true });
console.log(out + '.mp4', out + '.gif', n, 'frames');
