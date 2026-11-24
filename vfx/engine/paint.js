// Headless brush painter for Roblox battlegrounds-style VFX sprite sheets.
// Drawings are built from brush MARKS (tapered ribbons, polygons, dots) painted with Canvas2D,
// plus pixel fills for soft media (mist, dust, fire). Layered drawings export four WHITE sheets:
//   glow = blurred body (soft halo, LightEmission 1)
//   rim  = marks drawn wider by `rim` (outline / dark ink edge)
//   mid  = the marks themselves (body)
//   core = marks flagged `hot` (drawn at core width) + `coreOnly` marks (bright strands, teeth, tone)
// Colour comes from each ParticleEmitter's Color, so one sheet can be blue energy, pink, or black ink.
(function (G) {
  'use strict';

  // ---------- math ----------
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function Noise(seed) {
    const r = rng(seed), N = 256, g = new Float32Array(N * N);
    for (let i = 0; i < g.length; i++) g[i] = r();
    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
      const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
      const x0 = xi & 255, y0 = yi & 255, x1 = (x0 + 1) & 255, y1 = (y0 + 1) & 255;
      const a = g[y0 * N + x0], b = g[y0 * N + x1], c = g[y1 * N + x0], d = g[y1 * N + x1];
      return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
    };
  }
  const fbm = (n, x, y, o) => { let s = 0, a = 0.5, f = 1, t = 0; for (let i = 0; i < (o || 4); i++) { s += a * n(x * f, y * f); t += a; a *= 0.5; f *= 2.03; } return s / t; };
  const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
  const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const seq = (arr, i) => arr[Math.min(arr.length - 1, Math.max(0, i))];
  const lerp = (a, b, t) => a + (b - a) * t;
  const TAU = Math.PI * 2;
  const NA = Noise(3), NB = Noise(17), NC = Noise(29);

  // ---------- marks ----------
  const ribbon = (pts, w, o) => Object.assign({ t: 'ribbon', pts, w }, o || {});
  const poly = (pts, o) => Object.assign({ t: 'poly', pts }, o || {});
  const dot = (x, y, r, o) => Object.assign({ t: 'dot', x, y, r }, o || {});
  function arcPts(cx, cy, r, a0, a1, n, rf) {
    const P = [];
    for (let k = 0; k <= n; k++) { const u = k / n, a = lerp(a0, a1, u), rr = rf ? rf(u) : r; P.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); }
    return P;
  }
  // width profile: 0 at both ends, peak `w` at `peak` (0..1), tip sharpness `p`
  const taper = (n, w, peak, p) => Array.from({ length: n + 1 }, (_, k) => {
    const u = k / n, s = u < peak ? u / peak : (1 - u) / (1 - peak);
    return w * Math.pow(clamp(s, 0, 1), p || 0.7);
  });
  const linePts = (x0, y0, x1, y1, n) => Array.from({ length: n + 1 }, (_, k) => [lerp(x0, x1, k / n), lerp(y0, y1, k / n)]);

  // ---------- rendering ----------
  function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h || w; return c; }
  function drawMark(ctx, m, X, Y, S, extra, wscale) {
    ctx.globalAlpha = m.a === undefined ? 1 : m.a;
    ctx.fillStyle = '#fff'; ctx.strokeStyle = '#fff';
    const ws = wscale || 1;
    if (m.t === 'dot') {
      const r = m.r * ws + extra;
      if (r <= 0) return;
      ctx.beginPath(); ctx.arc(X(m.x), Y(m.y), r * S, 0, TAU); ctx.fill();
    } else if (m.t === 'poly') {
      ctx.beginPath(); m.pts.forEach(([x, y], k) => (k ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)))); ctx.closePath(); ctx.fill();
      if (extra > 0) { ctx.lineWidth = extra * 2 * S; ctx.lineJoin = 'miter'; ctx.miterLimit = 8; ctx.stroke(); }
    } else {
      const P = m.pts, n = P.length; if (n < 2) return;
      const W = (k) => { const w = Array.isArray(m.w) ? m.w[k] : m.w; return Math.max(0, w * ws + extra * Math.min(1, w / 0.006 + 0.25)); };
      const L = [], R = [];
      for (let k = 0; k < n; k++) {
        const a = P[Math.max(0, k - 1)], b = P[Math.min(n - 1, k + 1)];
        let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
        const w = W(k);
        L.push([P[k][0] - dy * w, P[k][1] + dx * w]); R.push([P[k][0] + dy * w, P[k][1] - dx * w]);
      }
      ctx.beginPath();
      L.forEach(([x, y], k) => (k ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y))));
      for (let k = n - 1; k >= 0; k--) ctx.lineTo(X(R[k][0]), Y(R[k][1]));
      ctx.closePath(); ctx.fill();
    }
  }
  function paintCell(ctx, marks, ox, oy, cell, extra, filter, wsFor) {
    const S = cell / 2, X = (x) => ox + (x + 1) * S, Y = (y) => oy + (1 - y) * S, pad = cell * 0.03;
    ctx.save(); ctx.beginPath(); ctx.rect(ox + pad, oy + pad, cell - 2 * pad, cell - 2 * pad); ctx.clip();
    for (const m of marks) if (!filter || filter(m)) drawMark(ctx, m, X, Y, S, extra, wsFor ? wsFor(m) : 1);
    ctx.restore();
  }
  // blur one cell into `dst` (cells blurred separately so frames never bleed)
  function blurCell(dst, src, ox, oy, cell, px, gain) {
    const tmp = canvas(cell), t = tmp.getContext('2d');
    t.filter = `blur(${px}px)`;
    t.drawImage(src, ox, oy, cell, cell, 0, 0, cell, cell);
    const pad = cell * 0.03, g = dst.getContext('2d');
    g.save(); g.globalAlpha = 1; g.beginPath(); g.rect(ox + pad, oy + pad, cell - 2 * pad, cell - 2 * pad); g.clip();
    for (let k = 0; k < (gain || 1); k++) g.drawImage(tmp, ox, oy);
    g.restore();
  }

  function layered(def) {
    const size = def.size || 1024, g = def.grid || 4, n = def.frames || g * g, cell = size / g;
    const out = { glow: canvas(size), rim: canvas(size), mid: canvas(size), core: canvas(size) };
    const cx = { rim: out.rim.getContext('2d'), mid: out.mid.getContext('2d'), core: out.core.getContext('2d') };
    const src = canvas(size), sx = src.getContext('2d');
    for (let i = 0; i < n; i++) {
      const ox = (i % g) * cell, oy = Math.floor(i / g) * cell;
      const marks = def.frame(i, n);
      const body = (m) => !m.coreOnly && !m.glowOnly;
      paintCell(cx.mid, marks, ox, oy, cell, 0, body);
      paintCell(cx.rim, marks, ox, oy, cell, def.rim || 0.02, (m) => body(m) && !m.noRim);
      paintCell(cx.core, marks, ox, oy, cell, 0, (m) => m.hot || m.coreOnly, (m) => (m.coreOnly ? 1 : m.coreW !== undefined ? m.coreW : def.coreW || 0.45));
      sx.clearRect(ox, oy, cell, cell);
      paintCell(sx, marks, ox, oy, cell, 0, (m) => body(m) || m.glowOnly);
      blurCell(out.glow, src, ox, oy, cell, (def.glow || 0.08) * cell / 2, def.glowGain || 2);
    }
    return out;
  }
  function single(def) {
    const size = def.size || 512, g = def.grid || 1, n = def.frames || g * g, cell = size / g;
    const c = canvas(size), ctx = c.getContext('2d'), src = canvas(size), sx = src.getContext('2d');
    for (let i = 0; i < n; i++) {
      const ox = (i % g) * cell, oy = Math.floor(i / g) * cell;
      const marks = def.frame(i, n);
      if (def.halo) { sx.clearRect(ox, oy, cell, cell); paintCell(sx, marks, ox, oy, cell, 0, null); blurCell(c, src, ox, oy, cell, def.halo * cell / 2, 1); }
      paintCell(ctx, marks, ox, oy, cell, 0, (m) => !m.glowOnly);
    }
    return c;
  }
  // pixel painter for soft media: frame(i, f) -> (x, y) => [value 0-1, alpha 0-1]
  function pixels(def) {
    const size = def.size || 1024, g = def.grid || 4, n = g * g, cell = size / g;
    const c = canvas(size), ctx = c.getContext('2d'), img = ctx.createImageData(size, size), d = img.data;
    for (let i = 0; i < n; i++) {
      const ox = (i % g) * cell, oy = Math.floor(i / g) * cell, f = n > 1 ? i / (n - 1) : 0, fn = def.frame(i, f);
      for (let py = 0; py < cell; py++) for (let px = 0; px < cell; px++) {
        const x = ((px + 0.5) / cell) * 2 - 1, y = 1 - ((py + 0.5) / cell) * 2;
        const edge = clamp((0.97 - Math.max(Math.abs(x), Math.abs(y))) / 0.06, 0, 1);
        const [v, a] = fn(x, y);
        const k = ((oy + py) * size + ox + px) * 4;
        d[k] = d[k + 1] = d[k + 2] = clamp(v, 0, 1) * 255; d[k + 3] = clamp(a, 0, 1) * edge * 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return c;
  }
  // scalar field h (>0 inside) -> four layers via thresholds (soft media with a hard-ish core)
  function pixelLayers(def) {
    const size = def.size || 1024, g = def.grid || 4, n = g * g, cell = size / g;
    const names = ['glow', 'rim', 'mid', 'core'], out = {}, buf = {};
    for (const k of names) { out[k] = canvas(size); buf[k] = out[k].getContext('2d').createImageData(size, size); }
    const T = def.th;
    for (let i = 0; i < n; i++) {
      const ox = (i % g) * cell, oy = Math.floor(i / g) * cell, f = i / (n - 1), fn = def.frame(i, f);
      for (let py = 0; py < cell; py++) for (let px = 0; px < cell; px++) {
        const x = ((px + 0.5) / cell) * 2 - 1, y = 1 - ((py + 0.5) / cell) * 2;
        const edge = clamp((0.95 - Math.max(Math.abs(x), Math.abs(y))) / 0.08, 0, 1);
        const h = fn(x, y), k = ((oy + py) * size + ox + px) * 4, s = T.soft;
        const A = [Math.pow(clamp((h - T.glow) / (T.mid - T.glow), 0, 1), 1.6), smooth(T.rim - s, T.rim + s, h), smooth(T.mid - s, T.mid + s, h), smooth(T.core - s, T.core + s, h)];
        for (let L = 0; L < 4; L++) { const b = buf[names[L]].data; b[k] = b[k + 1] = b[k + 2] = 255; b[k + 3] = A[L] * edge * 255; }
      }
    }
    for (const k of names) out[k].getContext('2d').putImageData(buf[k], 0, 0);
    return out;
  }
  // manga screentone dots, radius from rf(x, y) in 0..1
  function halftone(x0, y0, x1, y1, step, rf, o) {
    const M = [];
    let row = 0;
    for (let y = y0; y <= y1; y += step, row++) for (let x = x0 + (row % 2) * step / 2; x <= x1; x += step) {
      const r = rf(x, y); if (r > 0.05) M.push(dot(x, y, r * step * 0.5, o));
    }
    return M;
  }

  // ======================================================================
  // DRAWINGS (cell space x,y in [-1,1], y up; keep inside ~0.92)
  // ======================================================================

  // ---- energy crescent made of strands (video 1 blue arcs, video 3 wind trails) ----
  function strandArc(opt) {
    const r = rng(opt.seed), R = opt.R || 0.78, A0 = opt.a0, SW = opt.sweep, NS = opt.strands || 46;
    const head = opt.head || [0.5, 0.9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
    const tail = opt.tail || [0, 0, 0, 0.03, 0.09, 0.17, 0.26, 0.36, 0.46, 0.56, 0.65, 0.74, 0.82, 0.89, 0.94, 0.98];
    const Tm = opt.thick || [0.3, 0.4, 0.42, 0.41, 0.38, 0.34, 0.3, 0.26, 0.22, 0.18, 0.15, 0.12, 0.09, 0.065, 0.045, 0.025];
    const bodyA = opt.bodyA === undefined ? 0.9 : opt.bodyA;
    const S = Array.from({ length: NS }, () => {
      const q = Math.pow(r(), 1.5); // 0 = cutting edge; dense near the edge, sparse wisps inside
      return { q, s0: r() * 0.45 * (0.3 + q), s1: 1 - r() * 0.25 * q, w: (0.004 + r() * 0.016) * (1.2 - q * 0.7), ph: r() * TAU,
        spin: (0.15 + r() * 0.5) * q, hot: q < 0.22 && r() < 0.7, a: 0.55 + r() * 0.45 };
    });
    const FLECK = Array.from({ length: 16 }, () => ({ s: r(), d: -0.05 + r() * 0.15, l: 0.04 + r() * 0.12, b: 2 + Math.floor(r() * 9) }));
    return (i) => {
      const h = seq(head, i), t = seq(tail, i), T = seq(Tm, i), M = [];
      const th = (u) => T * Math.pow(Math.sin(Math.PI * clamp(u * 0.92 + 0.04, 0, 1)), 0.6) * (0.35 + 0.8 * u);
      const ang = (sv) => A0 - sv * SW;
      // solid swoosh body: white band hugging the cutting edge
      if (h - t > 0.05) {
        const P = [], W = [];
        for (let k = 0; k <= 60; k++) {
          const u = k / 60, sv = lerp(t, h, u), w = th(u) * 0.24;
          P.push([Math.cos(ang(sv)) * (R - w), Math.sin(ang(sv)) * (R - w)]); W.push(w);
        }
        M.push(ribbon(P, W, { hot: true, coreW: 0.6, a: bodyA }));
      }
      for (const s of S) { // hair strands that spiral inward
        const a = Math.max(s.s0, t), b = Math.min(s.s1, h);
        if (b - a < 0.04) continue;
        const N = 44, P = [], W = [];
        for (let k = 0; k <= N; k++) {
          const lu = k / N, sv = lerp(a, b, lu), u = (sv - t) / Math.max(0.05, h - t);
          const rr = R - th(u) * (s.q + s.spin * (1 - lu)) + Math.sin(sv * 11 + s.ph + i * 0.9) * 0.007 * (0.5 + s.q * 3);
          P.push([Math.cos(ang(sv)) * rr, Math.sin(ang(sv)) * rr]);
          W.push(s.w * Math.pow(Math.sin(Math.PI * lu), 0.5) * clamp(T / 0.3, 0.3, 1.15));
        }
        M.push(ribbon(P, W, { hot: s.hot, coreW: 0.45, a: s.a * (1 - s.q * 0.4) }));
      }
      for (const f of FLECK) { // flecks and dashes thrown off
        if (i < f.b || i > f.b + 5 || f.s < t || f.s > h) continue;
        const age = (i - f.b) / 5, an = ang(f.s), rr = R + f.d + age * 0.12, ta = an - Math.PI / 2;
        const x = Math.cos(an) * rr, y = Math.sin(an) * rr, l = f.l * (1 - age * 0.5);
        M.push(ribbon(linePts(x, y, x + Math.cos(ta) * l, y + Math.sin(ta) * l, 6), taper(6, 0.01 * (1 - age * 0.5), 0.3, 0.8), { hot: true }));
      }
      return M;
    };
  }

  // ---- black calligraphic ink crescent with needle tips, hook and barbs ----
  function inkArc(seed) {
    const r = rng(seed), R = 0.78, A0 = (200 * Math.PI) / 180, SW = (170 * Math.PI) / 180;
    const barbs = Array.from({ length: 4 }, () => ({ u: 0.2 + r() * 0.6, l: 0.06 + r() * 0.08 }));
    return (i) => {
      const head = seq([0.55, 0.9, 1], i), tail = seq([0, 0, 0, 0, 0, 0, 0.02, 0.08, 0.16, 0.26, 0.37, 0.48, 0.6, 0.72, 0.84, 0.95], i);
      const wm = seq([0.7, 1, 1, 1, 0.97, 0.92, 0.86, 0.78, 0.68, 0.58, 0.48, 0.38, 0.28, 0.2, 0.12, 0.06], i);
      const M = [], N = 60, P = [], W = [];
      for (let k = 0; k <= N; k++) {
        const u = k / N, sv = lerp(tail, head, u), ang = A0 - sv * SW;
        const w = 0.075 * wm * Math.pow(Math.sin(Math.PI * clamp(u, 0, 1)), 1.1) * (0.6 + 0.8 * u) + 0.0015;
        const rr = R + Math.sin(sv * 7 + i * 0.4) * 0.008 - w * 0.4;
        P.push([Math.cos(ang) * rr, Math.sin(ang) * rr]); W.push(w);
      }
      M.push(ribbon(P, W));
      if (head > 0.8 && wm > 0.3) { // reverse hook at the head
        const ang = A0 - head * SW, x = Math.cos(ang) * R * 0.97, y = Math.sin(ang) * R * 0.97, ba = ang + Math.PI * 0.62;
        M.push(ribbon(linePts(x, y, x + Math.cos(ba) * 0.2 * wm, y + Math.sin(ba) * 0.2 * wm, 10), taper(10, 0.028 * wm, 0.15, 0.8)));
      }
      for (const b of barbs) {
        const sv = lerp(tail, head, b.u); if (sv < tail + 0.05) continue;
        const ang = A0 - sv * SW, rr = R - 0.06 * wm, x = Math.cos(ang) * rr, y = Math.sin(ang) * rr, ba = ang + Math.PI + 0.5;
        M.push(ribbon(linePts(x, y, x + Math.cos(ba) * b.l * wm, y + Math.sin(ba) * b.l * wm, 6), taper(6, 0.016 * wm, 0.1, 0.9)));
      }
      return M;
    };
  }

  // ---- curved serrated blade with comb teeth + screentone (video 1 navy shards) ----
  function sawFan(i) {
    const open = seq([0.4, 0.75, 0.95, 1, 1, 1, 1, 1, 0.97, 0.93, 0.87, 0.79, 0.69, 0.57, 0.43, 0.28], i);
    const wm = seq([0.7, 1, 1, 1, 1, 0.97, 0.93, 0.88, 0.82, 0.74, 0.65, 0.55, 0.44, 0.33, 0.22, 0.12], i);
    const cx = -0.25, cy = -1.05, Ro = 1.6, A0 = 2.25, SW = 1.25 * open, teeth = 18, M = [];
    const thick = (u) => 0.95 * wm * Math.pow(Math.sin(Math.PI * clamp(u, 0, 1)), 0.7) * (0.5 + 0.7 * u);
    const outer = [], inner = [];
    for (let k = 0; k <= teeth * 2; k++) {
      const u = k / (teeth * 2), a = A0 - u * SW, T = thick(u), tl = T * 0.42 * (0.7 + 0.3 * Math.sin(k * 2.3));
      const rr = k % 2 ? Ro - tl : Ro + (k % 4 === 0 ? 0.015 : 0);
      outer.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
      inner.push([cx + Math.cos(a) * (Ro - T), cy + Math.sin(a) * (Ro - T)]);
    }
    M.push(poly([...outer, ...inner.reverse()]));
    for (let k = 0; k < teeth; k++) { // white teeth: thin needles along the serrated edge
      const u = (k * 2) / (teeth * 2), a = A0 - u * SW, T = thick(u); if (T < 0.02) continue;
      const a2 = A0 - ((k * 2 + 1) / (teeth * 2)) * SW, tl = T * 0.42;
      M.push(poly([[cx + Math.cos(a) * Ro, cy + Math.sin(a) * Ro], [cx + Math.cos(a2) * (Ro - tl), cy + Math.sin(a2) * (Ro - tl)],
        [cx + Math.cos(a2) * (Ro - tl * 1.5), cy + Math.sin(a2) * (Ro - tl * 1.5)], [cx + Math.cos(a) * (Ro - tl * 0.4), cy + Math.sin(a) * (Ro - tl * 0.4)]], { coreOnly: true }));
    }
    M.push(...halftone(-0.92, -0.92, 0.92, 0.92, 0.05, (x, y) => {
      const d = Math.hypot(x - cx, y - cy), a = Math.atan2(y - cy, x - cx), u = (A0 - a) / Math.max(0.01, SW);
      if (u < 0.05 || u > 0.95) return 0;
      const T = thick(u); if (d > Ro - T * 0.55 || d < Ro - T * 0.95) return 0;
      return smooth(Ro - T * 0.95, Ro - T * 0.6, d) * 0.85;
    }, { coreOnly: true }));
    return M;
  }

  // ---- 4-point star (video 1 navy star) ----
  function star4(i) {
    const s = [0.6, 1, 0.82, 0.5][i], rot = [0, 0.05, 0.09, 0.12][i], M = [], arms = [], inner = 0.13 * s;
    for (let k = 0; k < 8; k++) {
      const a = rot + (k * Math.PI) / 4 + Math.PI / 4, rr = k % 2 ? inner : 0.9 * s * (k % 4 === 0 ? 1 : 0.9);
      arms.push([Math.cos(a) * rr, Math.sin(a) * rr]);
    }
    M.push(poly(arms));
    for (let k = 0; k < 4; k++) {
      const a = rot + (k * Math.PI) / 2 + Math.PI / 4;
      M.push(ribbon(linePts(0, 0, Math.cos(a) * 0.88 * s, Math.sin(a) * 0.88 * s, 12), taper(12, 0.028 * s, 0.05, 0.9), { coreOnly: true }));
    }
    M.push(dot(0, 0, 0.07 * s, { coreOnly: true }));
    return M;
  }

  function glint(i) {
    const s = [0.45, 1, 0.7, 0.35][i], M = [dot(0, 0, 0.06 * s), dot(0, 0, 0.12 * s, { glowOnly: true })];
    for (let k = 0; k < 4; k++) {
      const a = (k * Math.PI) / 2, b = a + Math.PI / 4;
      M.push(ribbon(linePts(0, 0, Math.cos(a) * 0.95 * s, Math.sin(a) * 0.95 * s, 14), taper(14, 0.045 * s, 0.02, 1.2)));
      M.push(ribbon(linePts(0, 0, Math.cos(b) * 0.3 * s, Math.sin(b) * 0.3 * s, 8), taper(8, 0.022 * s, 0.02, 1.1)));
    }
    return M;
  }
  const line = () => [ribbon(linePts(0, -0.95, 0, 0.95, 30), taper(30, 0.011, 0.5, 0.3))];
  const spark = () => [ribbon(linePts(0, -0.92, 0, 0.92, 20), taper(20, 0.055, 0.72, 0.6)), dot(0, 0.35, 0.12, { glowOnly: true })];

  // ---- top-down vortex (ground swirl, ring slash) ----
  function swirl(opt) {
    const r = rng(opt.seed), N = opt.n || 12;
    const A = Array.from({ length: N }, () => ({ r0: opt.rmin + r() * (opt.rmax - opt.rmin), a0: r() * TAU, len: opt.lmin + r() * (opt.lmax - opt.lmin), w: opt.w * (0.4 + r() * 0.9), hot: r() < opt.hot, dr: (r() - 0.5) * opt.spiral }));
    return (i) => {
      const grow = seq(opt.grow, i), fade = seq(opt.fade, i), spin = i * opt.spin, M = [];
      for (const s of A) {
        const len = s.len * grow, a0 = s.a0 + spin, P = arcPts(0, 0, s.r0, a0, a0 - len, 40, (u) => s.r0 + s.dr * u);
        M.push(ribbon(P, taper(40, s.w * fade, 0.62, 0.7), { hot: s.hot, coreW: 0.35 }));
      }
      return M;
    };
  }

  function inkSpikes(i) {
    const r = rng(71), M = [], g = [0.65, 1, 1, 0.9][i], w = [1, 1, 0.65, 0.35][i], st = [0, 0, 0.12, 0.3][i];
    for (let k = 0; k < 30; k++) {
      const a = (k / 30) * TAU + (r() - 0.5) * 0.2, L = (0.45 + r() * 0.5) * g, r0 = 0.12 + st * L;
      const kink = (r() - 0.5) * 0.25, mid = 0.4 + r() * 0.3, P = [], W = taper(16, (0.02 + r() * 0.035) * w, 0.12, 0.9);
      for (let j = 0; j <= 16; j++) { const u = j / 16, rr = r0 + (L - r0) * u, aa = a + (u > mid ? kink * (u - mid) : 0); P.push([Math.cos(aa) * rr, Math.sin(aa) * rr]); }
      M.push(ribbon(P, W));
    }
    for (let k = 0; k < 3; k++) M.push(ribbon(arcPts(0, 0, 0.16 + k * 0.05, k, k + 2.2 + r() * 2, 30), taper(30, 0.014 * w, 0.5, 0.6)));
    return M;
  }

  function blobs(i) {
    const r = rng(83), M = [];
    for (let k = 0; k < 8; k++) {
      const x = (r() - 0.5) * 1.0, y = (r() - 0.5) * 0.7, R0 = 0.16 + r() * 0.18, birth = r() * 3, die = 9 + r() * 6;
      const life = smooth(birth, birth + 2.5, i) * (1 - smooth(die - 3, die, i)), R = R0 * (0.6 + 0.4 * life) * (life > 0.02 ? 1 : 0);
      if (R <= 0.01) continue;
      const yy = y + i * 0.01;
      M.push(dot(x, yy, R));
      M.push(ribbon(arcPts(x, yy, R * 0.82, 1.9, 3.9, 20), taper(20, R * 0.09, 0.5, 0.8), { coreOnly: true }));
      M.push(dot(x + R * 0.35, yy + R * 0.4, R * 0.1, { coreOnly: true }));
    }
    return M;
  }

  function flare() {
    const r = rng(91), M = [dot(0, 0, 0.1), dot(0, 0, 0.26, { glowOnly: true, a: 0.7 })];
    for (let k = 0; k < 40; k++) { const a = r() * TAU, L = 0.35 + r() * 0.6; M.push(ribbon(linePts(0, 0, Math.cos(a) * L, Math.sin(a) * L, 10), taper(10, 0.006 + r() * 0.01, 0.05, 1), { a: 0.5 + r() * 0.5 })); }
    M.push(ribbon(linePts(-0.95, 0, 0.95, 0, 30), taper(30, 0.02, 0.5, 1.4)));
    return M;
  }
  const sparkle = (i) => { const s = [1, 0.55, 0.8, 0.35][i]; return [dot(0, 0, 0.22 * s), ...[0, 1, 2, 3].map((k) => ribbon(linePts(0, 0, Math.cos(k * Math.PI / 2) * 0.9 * s, Math.sin(k * Math.PI / 2) * 0.9 * s, 8), taper(8, 0.09 * s, 0.02, 1.1)))]; };

  // ---------- soft media ----------
  function mist(i, f) {
    const sc = 0.85 + f * 0.25;
    return (x, y) => {
      const d = Math.hypot(x / sc, (y + 0.05 - f * 0.1) / (sc * 0.8));
      const n = fbm(NA, x * 1.6 + 4 + f * 0.8, y * 1.6 - f * 1.2, 5), n2 = fbm(NB, x * 4.5 - f, y * 4.5 + f * 2, 3);
      const dens = (1 - d) * 1.2 + (n - 0.5) * 1.6 + (n2 - 0.5) * 0.7 - f * 0.85;
      return [0.8 + n2 * 0.2, smooth(-0.05, 0.6, dens) * 0.8];
    };
  }
  function dust(i, f) {
    const sc = 0.8 + f * 0.25;
    return (x, y) => {
      const d = Math.hypot(x / sc, (y + 0.1) / (sc * 0.72));
      const n = fbm(NC, x * 2.2 + 9, y * 2.2 - f * 0.7, 5);
      const dens = (1 - d) * 1.5 + (n - 0.5) * 1.2 - f * 1.0;
      return [clamp(0.62 + y * 0.35 + (n - 0.5) * 0.5, 0.3, 1), smooth(0.0, 0.3, dens) * 0.9];
    };
  }
  const bokeh = () => (x, y) => { const d = Math.hypot(x, y); return [1, Math.max(smooth(0.3, 0.12, d), Math.pow(clamp(1 - d / 0.92, 0, 1), 2.4) * 0.7)]; };
  function fireBurst(i, f) {
    const R = 0.2 + 0.5 * (1 - Math.pow(1 - Math.min(1, f * 4), 2)), er = Math.max(0, (f - 0.35) / 0.65);
    return (x, y) => {
      const d = Math.hypot(x, y), a = Math.atan2(y, x);
      const spikes = fbm(NB, Math.cos(a) * 3 + 7, Math.sin(a) * 3 + i * 0.3, 4);
      const n = fbm(NA, x * 3 + i * 0.4, y * 3 - i * 0.5, 4);
      return 1 - d / (R * (0.75 + spikes * 0.55)) + (n - 0.5) * 0.45 - er * (0.6 + n * 0.9);
    };
  }

  // ---------- registry ----------
  const D = (deg) => (deg * Math.PI) / 180;
  const DEFS = {
    wisp_arc: { kind: 'layered', grid: 4, rim: 0.01, glow: 0.07, coreW: 0.45, frame: strandArc({ seed: 5, a0: D(210), sweep: D(220) }), note: 'Energy crescent of brush strands' },
    trail_arc: { kind: 'layered', grid: 4, rim: 0.008, glow: 0.06, coreW: 0.4, frame: strandArc({ seed: 9, R: 0.84, a0: D(200), sweep: D(205), strands: 60, bodyA: 0.55, thick: [0.24, 0.3, 0.32, 0.31, 0.29, 0.26, 0.23, 0.2, 0.17, 0.14, 0.11, 0.085, 0.065, 0.045, 0.03, 0.018] }), note: 'Wind slash trail: thin, many strands' },
    saw_fan: { kind: 'layered', grid: 4, rim: 0.016, glow: 0.05, frame: sawFan, note: 'Sawtooth fan with comb teeth + screentone' },
    star4: { kind: 'layered', grid: 2, size: 1024, rim: 0.03, glow: 0.12, frame: star4, note: '4-point star flash' },
    ring_slash: { kind: 'layered', grid: 4, rim: 0.016, glow: 0.06, coreW: 0.3, frame: swirl({ seed: 33, n: 30, rmin: 0.42, rmax: 0.86, lmin: 2.2, lmax: 5.6, w: 0.075, hot: 0.3, spiral: 0.12, spin: -0.5, grow: [0.25, 0.6, 0.9, 1, 1, 1, 1, 1, 0.95, 0.88, 0.78, 0.66, 0.52, 0.38, 0.24, 0.1], fade: [0.7, 1, 1, 1, 1, 0.95, 0.88, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.22, 0.14, 0.07] }), note: 'Vortex ring slash' },
    swirl_disk: { kind: 'layered', grid: 4, rim: 0.01, glow: 0.06, coreW: 0.35, frame: swirl({ seed: 21, n: 16, rmin: 0.2, rmax: 0.88, lmin: 1.2, lmax: 3.2, w: 0.035, hot: 0.4, spiral: 0.25, spin: 0.35, grow: [0.3, 0.7, 1, 1, 1, 1, 1, 1, 1, 0.95, 0.9, 0.8, 0.7, 0.55, 0.4, 0.25], fade: [0.8, 1, 1, 1, 1, 1, 0.95, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15, 0.07] }), note: 'Top-down vortex swirl' },
    blobs: { kind: 'layered', grid: 4, rim: 0.02, glow: 0.08, frame: blobs, note: 'Bubbly glass energy blobs' },
    fire_burst: { kind: 'pixelLayers', grid: 4, th: { glow: -0.28, rim: -0.04, mid: 0.08, core: 0.55, soft: 0.05 }, frame: fireBurst, note: 'Fire flash burst' },
    ink_arc: { kind: 'single', grid: 4, size: 1024, frame: inkArc(13), note: 'Black calligraphic crescent (Color black, LightEmission 0)' },
    ink_spikes: { kind: 'single', grid: 2, size: 1024, frame: inkSpikes, note: 'Jagged ink spike burst' },
    glint: { kind: 'single', grid: 2, size: 512, halo: 0.07, frame: glint, note: 'Lens glint' },
    sparkle: { kind: 'single', grid: 2, size: 256, halo: 0.15, frame: sparkle, note: 'Twinkle sparkle (firework dots)' },
    line: { kind: 'single', grid: 1, size: 1024, halo: 0.012, frame: line, note: 'Thin straight line (tip = +Y)' },
    spark: { kind: 'single', grid: 1, size: 256, halo: 0.08, frame: spark, note: 'Glowing spark streak' },
    flare: { kind: 'single', grid: 1, size: 512, halo: 0.16, frame: flare, note: 'Lens-flare sun' },
    mist: { kind: 'pixels', grid: 4, size: 1024, frame: mist, note: 'Soft wispy mist' },
    dust: { kind: 'pixels', grid: 4, size: 1024, frame: dust, note: 'Value-shaded dust cloud' },
    bokeh: { kind: 'pixels', grid: 1, size: 128, frame: bokeh, note: 'Soft bokeh dot' },
  };
  const cache = {};
  G.VFXPaint = {
    defs: DEFS,
    layered: (name) => ['layered', 'pixelLayers'].includes(DEFS[name].kind),
    build(name) {
      if (cache[name]) return cache[name];
      const d = DEFS[name];
      if (!d) throw new Error('Unknown drawing ' + name);
      let o;
      if (d.kind === 'layered') o = layered(d);
      else if (d.kind === 'pixelLayers') o = pixelLayers(d);
      if (o) { const res = {}; for (const k of Object.keys(o)) res[`${name}_${k}`] = o[k]; return (cache[name] = res); }
      return (cache[name] = { [name]: d.kind === 'pixels' ? pixels(d) : single(d) });
    },
  };
})(typeof window !== 'undefined' ? window : globalThis);
