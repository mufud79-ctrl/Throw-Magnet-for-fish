// luaparse 0.3.1 is Lua 5.1-ish: rewrite Luau-only syntax before parsing (compound assignment, type annotations,
// `continue`, if-expressions are not used here).
const fs = require('fs'); const luaparse = require('luaparse');
for (const f of process.argv.slice(2)) {
  let src = fs.readFileSync(f, 'utf8');
  src = src.replace(/^--!.*$/m, '');
  src = src.replace(/([A-Za-z_][\w.\[\]"']*)\s*(\+|-|\*|\/|%|\.\.)=\s*/g, (m, lhs, op) => `${lhs} = ${lhs} ${op} `);
  try { luaparse.parse(src, { luaVersion: '5.3' }); console.log('OK', f); }
  catch (e) { console.log('FAIL', f, e.message); process.exitCode = 1; }
}
