// node build.mjs  -> lints every effect in effects/, then writes
//   out/lab.html                  (artifact page: all effects, PNG textures embedded)
//   out/<Name>/<Name>.lua         (ModuleScript per effect)
//   out/<Name>/textures.txt       (which PNGs from out/textures/ that effect needs)
// Run `python3 craft/textures.py` first whenever a texture recipe changes.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { lint } from './engine/lint.mjs';
const here = path.dirname(new URL(import.meta.url).pathname);
const read = (f) => fs.readFileSync(path.join(here, f), 'utf8');
const effectFiles = fs.readdirSync(path.join(here, 'effects')).filter((f) => f.endsWith('.js')).sort();
const ctx = {}; ctx.globalThis = ctx;
vm.runInNewContext(read('engine/spec.js'), ctx);
vm.runInNewContext(read('engine/luau.js'), ctx);
for (const f of effectFiles) vm.runInNewContext(read('effects/' + f), ctx);
const texDir = path.join(here, 'out', 'textures');
const have = new Set(fs.readdirSync(texDir).filter((f) => f.endsWith('.png') && !f.startsWith('_')).map((f) => f.slice(0, -4)));
let failed = false;
const used = new Set();
const all = Object.entries(ctx.VFX_EFFECTS).map(([n, fx]) => [n, fx, n]);
for (const [n, P] of Object.entries(ctx.VFX_PARTS || {})) all.push([n, ctx.VFXSpec.compose({ name: n, version: 1 }, [{ part: n, t: 0, at: [0, 0, 0], tag: n }]), path.join('parts', n)]);
for (const [name, fx, outName] of all) {
  const { errs, warn } = lint(fx, [...have]);
  warn.forEach((w) => console.warn(`warn ${name}: ${w}`));
  errs.forEach((e) => console.error(`ERROR ${name}: ${e}`));
  if (errs.length) { failed = true; continue; }
  const tex = [...new Set(fx.layers.map((l) => l.props.Texture))];
  tex.forEach((t) => used.add(t));
  const dir = path.join(here, 'out', outName.includes('parts') ? 'parts' : name);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, name + '.lua'), ctx.VFXLuau.toLuau(fx));
  if (!outName.includes('parts')) fs.writeFileSync(path.join(dir, 'textures.txt'), tex.map((t) => `out/textures/${t}.png`).join('\n') + '\n');
  console.log(`${name} v${fx.version}: ${fx.layers.length} emitters, ${tex.length} textures`);
}
if (failed) process.exit(1);
const texdata = {};
for (const t of [...used].sort()) texdata[t] = 'data:image/png;base64,' + fs.readFileSync(path.join(texDir, t + '.png')).toString('base64');
const scripts = [
  `window.VFX_TEXDATA = ${JSON.stringify(texdata)};`,
  read('engine/spec.js'), read('engine/sim.js'), read('engine/luau.js'),
  ...effectFiles.map((f) => read('effects/' + f)),
  read('viewer/app.js'),
].map((s) => `<script>\n${s}\n</script>`).join('\n');
const first = Object.values(ctx.VFX_EFFECTS)[0];
const html = read('viewer/shell.html').replace('{{TITLE}}', 'Anime VFX Lab').replace('{{NAME}}', first.name)
  .replace('{{VERSION}}', first.version).replace('{{SCRIPTS}}', () => scripts);
fs.writeFileSync(path.join(here, 'out', 'lab.html'), html);
console.log('out/lab.html', (html.length / 1024 / 1024).toFixed(2) + 'MB');
