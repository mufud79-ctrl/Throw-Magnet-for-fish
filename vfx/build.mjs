// node build.mjs <effect_file_basename>  ->  out/<Name>/<Name>.html (artifact page, single file)
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { lint } from './engine/lint.mjs';
const here = path.dirname(new URL(import.meta.url).pathname);
const file = process.argv[2] || 'fire_explosion';
const effectSrc = fs.readFileSync(path.join(here, 'effects', file + '.js'), 'utf8');
const ctx = { globalThis: {} }; ctx.globalThis = ctx; vm.runInNewContext(effectSrc, ctx);
const name = Object.keys(ctx.VFX_EFFECTS)[0];
const fx = ctx.VFX_EFFECTS[name];
const texSrc = fs.readFileSync(path.join(here, 'engine/textures.js'), 'utf8');
const texNames = [...texSrc.matchAll(/^    (\w+): \{ build:/gm)].map((m) => m[1]);
const { errs, warn } = lint(fx, texNames);
warn.forEach((w) => console.warn('warn:', w));
if (errs.length) { errs.forEach((e) => console.error('ERROR:', e)); process.exit(1); }
const parts = ['engine/textures.js', 'engine/sim.js', 'engine/luau.js'].map((f) => fs.readFileSync(path.join(here, f), 'utf8'));
parts.push(effectSrc, `window.VFX_ACTIVE = ${JSON.stringify(name)};`, fs.readFileSync(path.join(here, 'viewer/app.js'), 'utf8'));
const scripts = parts.map((s) => `<script>\n${s}\n</script>`).join('\n');
const html = fs.readFileSync(path.join(here, 'viewer/shell.html'), 'utf8')
  .replace('{{TITLE}}', `${name} VFX`).replace('{{NAME}}', name).replace('{{VERSION}}', fx.version)
  .replace('{{SCRIPTS}}', () => scripts);
const outDir = path.join(here, 'out', name);
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, name + '.html'), html);
console.log(path.join(outDir, name + '.html'), (html.length / 1024).toFixed(0) + 'KB');
