// Headless "paint" kit: draws anime VFX drawings as signed-distance shapes and splits each
// drawing into FOUR WHITE flipbook layers that stack in Roblox:
//   glow  (behind, stepped halo, LightEmission 1)
//   rim   (full silhouette; shows as the outline + interior cut lines)
//   mid   (silhouette inset by the rim width, minus cut lines)
//   core  (hottest region)
// All layers are white + alpha so Color/ColorSequence on each ParticleEmitter recolors them.
// Shapes are built from tapered tongues, lobes and arcs (designed shape language), with noise
// used only for boil (domain warp between drawings) and breakup, never as the shape itself.
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
  const fbm = (n, x, y, o) => { let s = 0, a = 0.5, f = 1, t = 0; for (let i = 0; i < (o || 3); i++) { s += a * n(x * f, y * f); t += a; a *= 0.5; f *= 2.03; } return s / t; };
  const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
  const aa = (x, w) => clamp(x / w + 0.5, 0, 1);
  const len = Math.hypot;
  const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const seq = (arr, i) => arr[Math.min(arr.length - 1, Math.max(0, i))];

  // ---------- SDF primitives (cell space: x,y in [-1,1], y up) ----------
  const circle = (x, y, cx, cy, r) => len(x - cx, y - cy) - r;
  function capsule(px, py, r1, r2, h) { // tapered capsule along +y, r2 = 0 -> sharp tip
    px = Math.abs(px);
    const b = (r1 - r2) / h, a = Math.sqrt(Math.max(0, 1 - b * b)), k = -b * px + a * py;
    if (k < 0) return len(px, py) - r1;
    if (k > a * h) return len(px, py - h) - r2;
    return a * px + b * py - r1;
  }
  // flame tongue: base (bx,by), angle from +y (clockwise +), length h, base/tip radius, bend = S/C curve
  function tongue(x, y, bx, by, ang, h, r1, r2, bend, wave) {
    const dx = x - bx, dy = y - by, c = Math.cos(ang), s = Math.sin(ang);
    const ly = dx * s + dy * c;
    let lx = dx * c - dy * s;
    const u = clamp(ly / h, 0, 1);
    lx -= bend * h * u * u + (wave || 0) * h * Math.sin(u * 5.5) * u;
    return capsule(lx, ly, r1, r2, h);
  }
  function smin(a, b, k) { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }

  // ---------- canvases ----------
  function canvas(size) { const c = document.createElement('canvas'); c.width = c.height = size; return c; }

  // Layered sheet: def.frame(i, n) -> sampler(x, y, s) that fills s.d (silhouette sdf), s.c (core sdf), s.k (cut sdf)
  function layered(def) {
    const size = def.size || 1024, g = def.grid || 4, n = def.frames || g * g, cell = size / g;
    const names = ['glow', 'rim', 'mid', 'core'];
    const out = {}, bufs = {};
    for (const k of names) { out[k] = canvas(size); bufs[k] = out[k].getContext('2d').createImageData(size, size); }
    const aw = (2 / cell) * 1.15, rimW = def.rim || 0.045, coreIn = def.coreInset || 0.05, gr = def.glow || 0.2;
    const s = { d: 1, c: 9, k: 9 };
    for (let i = 0; i < n; i++) {
      const samp = def.frame(i, n);
      const ox = (i % g) * cell, oy = Math.floor(i / g) * cell;
      for (let py = 0; py < cell; py++) {
        const y = 1 - ((py + 0.5) / cell) * 2;
        for (let px = 0; px < cell; px++) {
          const x = ((px + 0.5) / cell) * 2 - 1;
          s.d = 1; s.c = 9; s.k = 9;
          samp(x, y, s);
          const edge = Math.max(Math.abs(x), Math.abs(y));
          const d = Math.max(s.d, edge - 0.93);
          const idx = ((oy + py) * size + ox + px) * 4;
          const rim = aa(-d, aw);
          const mid = aa(-(d + rimW), aw) * (1 - aa(-s.k, aw));
          const core = aa(-Math.max(s.c, d + coreIn), aw);
          let glow = 1;
          if (d > 0) {
            const t = 1 - d / gr, w = aw / gr;
            glow = 0.42 * aa(t - 0.62, w) + 0.3 * aa(t - 0.3, w) + 0.28 * Math.pow(clamp(t, 0, 1), 2);
          }
          glow *= aa(0.97 - edge, aw);
          const A = [glow, rim, mid, core];
          for (let L = 0; L < 4; L++) {
            const b = bufs[names[L]].data;
            b[idx] = b[idx + 1] = b[idx + 2] = 255; b[idx + 3] = A[L] * 255;
          }
        }
      }
    }
    for (const k of names) out[k].getContext('2d').putImageData(bufs[k], 0, 0);
    return out;
  }

  // Single white mask sheet: sampler fills s.d and optional s.v (value 0-1, for shaded props)
  function mask(def) {
    const size = def.size || 512, g = def.grid || 1, n = def.frames || g * g, cell = size / g;
    const c = canvas(size), ctx = c.getContext('2d'), img = ctx.createImageData(size, size), b = img.data;
    const aw = (2 / cell) * 1.15, s = { d: 1, v: 1 };
    for (let i = 0; i < n; i++) {
      const samp = def.frame(i, n), ox = (i % g) * cell, oy = Math.floor(i / g) * cell;
      for (let py = 0; py < cell; py++) {
        const y = 1 - ((py + 0.5) / cell) * 2;
        for (let px = 0; px < cell; px++) {
          const x = ((px + 0.5) / cell) * 2 - 1;
          s.d = 1; s.v = 1; samp(x, y, s);
          s.d = Math.max(s.d, Math.max(Math.abs(x), Math.abs(y)) - 0.95);
          const idx = ((oy + py) * size + ox + px) * 4, v = s.v * 255;
          b[idx] = b[idx + 1] = b[idx + 2] = v; b[idx + 3] = aa(-s.d, aw) * 255;
        }
      }
    }
    ctx.putImageData(img, 0, 0);
    return c;
  }

  // ======================================================================
  // DRAWINGS
  // ======================================================================
  const NA = Noise(3), NB = Noise(17), NC = Noise(29), ND = Noise(53);

  // ---- ground fire blast: 16 drawings on 2s (12 fps) ----
  // lumpy multi-lobe dome + tongues leaning up/out; core = the same silhouette at ~55% scale, sunk toward the base
  const BLAST = (() => {
    const r = rng(8), T = [], Lb = [];
    const phis = [-1.32, -0.95, -0.6, -0.25, 0.08, 0.42, 0.78, 1.12, 1.4];
    phis.forEach((phi) => T.push({ phi: phi + (r() - 0.5) * 0.14, h: 0.24 + r() * 0.3 - Math.abs(phi) * 0.05, r1: 0.1 + r() * 0.06, bend: (r() - 0.5) * 1.0, ph: r() * 6.28, pinch: r() < 0.38 }));
    for (let k = 0; k < 7; k++) { const a = -1.35 + (k / 6) * 2.7 + (r() - 0.5) * 0.2; Lb.push({ a, d: 0.55 + r() * 0.2, r: 0.42 + r() * 0.2, ph: r() * 6.28 }); }
    return { T, Lb };
  })();
  function blastShape(i, x, y, P) {
    let d = 9;
    for (const l of P.lobes) d = smin(d, circle(x, y, l[0], l[1], l[2]), 0.03);
    for (const t of P.T) {
      if (t.h > 0.02) d = smin(d, tongue(x, y, t.bx, t.by, t.ang, t.h, t.r1, 0, t.bend, 0.08), 0.07);
      if (t.tipH > 0.01) d = Math.min(d, tongue(x, y, t.tx, t.ty, t.ang * 0.5, t.tipH, t.tipR, 0, t.bend * 0.5, 0));
    }
    return Math.max(d, -0.9 - y);
  }
  function blast(i) {
    const grow = seq([0.22, 0.46, 0.58, 0.63, 0.65, 0.65, 0.64, 0.62, 0.59, 0.55, 0.5, 0.45, 0.4, 0.34, 0.28, 0.22], i);
    const lenK = seq([0.55, 0.9, 1.1, 1.18, 1.15, 1.08, 0.98, 0.86, 0.75, 0.64, 0.54, 0.45, 0.36, 0.28, 0.2, 0.12], i);
    const cy = -0.9 + grow * 0.62 + Math.max(0, i - 5) * 0.028, R = grow;
    const det = Math.max(0, i - 4);
    const lobes = BLAST.Lb.map((l) => {
      const pul = 1 + 0.06 * Math.sin(i * 2.3 + l.ph);
      return [Math.sin(l.a) * R * l.d, cy + Math.cos(l.a) * R * l.d * 0.85, R * l.r * pul];
    });
    lobes.push([0, cy - R * 0.1, R * 0.82]);
    const T = BLAST.T.map((t) => {
      const ang = t.phi * 0.8, bx = Math.sin(t.phi) * R * 0.8, by = cy + Math.cos(t.phi) * R * 0.72;
      const h = t.h * lenK * (t.pinch && det > 0 ? Math.max(0.35, 1 - det / 6) : 1);
      const bend = t.bend + 0.4 * Math.sin(i * 1.9 + t.ph);
      const tipD = t.h * 1.05 + det * 0.05, tl = t.pinch && det > 0 ? 1 - det / 9 : 0;
      return { ang, bx, by, h, bend, r1: t.r1 * (0.55 + 0.45 * lenK),
        tx: bx + Math.sin(ang) * tipD, ty: Math.min(0.58, by + Math.cos(ang) * tipD + det * 0.03), tipH: 0.22 * tl, tipR: 0.095 * tl };
    });
    const P = { lobes, T }, CK = 0.56, base = -0.9;
    const coreOn = seq([1, 1, 1, 0.95, 0.85, 0.72, 0.58, 0.45, 0.32, 0.2, 0.1, 0], i);
    const erode = i < 7 ? -1 : (i - 7) / 8;
    return (x0, y0, s) => {
      const wx = (NA(x0 * 2.1 + i * 3.7, y0 * 2.1 - i * 0.6) - 0.5) * 0.12, wy = (NB(x0 * 2.1 - i * 2.3, y0 * 2.1 - i * 0.6) - 0.5) * 0.09;
      const x = x0 + wx, y = y0 + wy;
      let d = blastShape(i, x, y, P);
      const k = CK * coreOn;
      const c = k > 0.02 ? blastShape(i, x / k, (y - base) / k + base - 0.05, P) * k : 9;
      if (erode > 0) d = Math.max(d, (erode * 0.8 - fbm(NC, x0 * 2.6, y0 * 2.6 - i * 0.12)) * 0.6 + 0.1 * erode);
      s.d = d; s.c = c;
      if (i >= 2 && i <= 12) {
        const kk = Math.abs(fbm(ND, x * 2.3 + i * 0.05, y * 2.3 - i * 0.25) - 0.5) - 0.013;
        s.k = Math.max(kk, d + 0.1, -c + 0.03);
      }
    };
  }

  // ---- cel smoke cloud: lobes with crease lines, dissolves with round holes (on 3s) ----
  const SMOKE_L = (() => {
    const r = rng(41), L = [[0, -0.15, 0.36]];
    for (let k = 0; k < 9; k++) { const a = r() * 6.28, d = 0.22 + r() * 0.28; L.push([Math.cos(a) * d, Math.sin(a) * d * 0.75 - 0.05, 0.17 + r() * 0.15, 8 + r() * 7]); }
    L[0].push(15);
    return L;
  })();
  const SMOKE_H = (() => { const r = rng(43), H = []; for (let k = 0; k < 14; k++) H.push([(r() - 0.5) * 1.3, (r() - 0.5) * 1.0, 3 + r() * 9]); return H; })();
  function smoke(i) {
    const sc = 0.72 + 0.28 * smooth(0, 6, i), rise = i * 0.022;
    const lobes = SMOKE_L.map(([x, y, r, die]) => [x * sc, y * sc + rise, r * sc * Math.pow(clamp((die - i) / 5, 0, 1), 0.6)]).filter((l) => l[2] > 0.005);
    const holes = SMOKE_H.map(([x, y, st]) => [x * sc, y * sc + rise, Math.max(0, i - st) * 0.045]);
    const L = [-0.55, 0.62];
    return (x, y, s) => {
      let d1 = 9, d2 = 9, dl = 9;
      for (const [cx, cy, r] of lobes) {
        const dd = circle(x, y, cx, cy, r);
        if (dd < d1) { d2 = d1; d1 = dd; } else if (dd < d2) d2 = dd;
        dl = Math.min(dl, circle(x, y, cx + L[0] * r * 0.34, cy + L[1] * r * 0.34, r * 0.72));
      }
      let d = smin(d1, d2, 0.035);
      for (const [hx, hy, hr] of holes) if (hr > 0) d = Math.max(d, -circle(x, y, hx, hy, hr));
      s.d = d; s.c = Math.max(dl, d + 0.03);
      if (d2 < 0) s.k = Math.abs(d2 - d1) - 0.011;
    };
  }

  // ---- impact flash star (2x2) ----
  const RAYS = (() => { const r = rng(12), R = []; for (let k = 0; k < 13; k++) R.push([(k + (r() - 0.5) * 0.6) / 13 * 6.283, 0.5 + r() * 0.45, 0.05 + r() * 0.035]); return R; })();
  function flash(i) {
    const lk = [0.62, 1, 0.95, 0.7][i], th = [1.1, 0.85, 0.45, 0.25][i], disc = [0.26, 0.2, 0.08, -1][i], start = [0, 0, 0.3, 0.55][i];
    return (x, y, s) => {
      let d = circle(x, y, 0, 0, disc), c = circle(x, y, 0, 0, disc * 0.55);
      for (const [a, L, w] of RAYS) {
        const b0 = start * L;
        d = Math.min(d, tongue(x, y, Math.sin(a) * b0, Math.cos(a) * b0, a, Math.max(0.01, L * lk - b0), w * th, 0, 0, 0));
        if (i < 2) c = Math.min(c, tongue(x, y, 0, 0, a, L * lk * 0.5, w * th * 0.35, 0, 0, 0));
      }
      s.d = d; s.c = c;
    };
  }

  // ---- crescent slash. kind: 'steel' (clean, streaked) or 'fire' (flame tongues trail off the edge) ----
  function slashDrawing(kind) {
    const fire = kind === 'fire';
    const R = fire ? 0.64 : 0.8, A0 = (215 * Math.PI) / 180, SW = (250 * Math.PI) / 180;
    const head = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
    const tail = [0, 0, 0, 0.03, 0.1, 0.2, 0.33, 0.44, 0.54, 0.63, 0.71, 0.78, 0.85, 0.9, 0.95, 0.99];
    const tmax = (fire ? [0.05, 0.22, 0.24, 0.23, 0.2, 0.17, 0.14, 0.11, 0.09, 0.07, 0.055, 0.04, 0.03, 0.02, 0.012, 0.006]
      : [0.045, 0.2, 0.22, 0.2, 0.17, 0.13, 0.1, 0.075, 0.055, 0.042, 0.032, 0.024, 0.017, 0.011, 0.007, 0.004]);
    const r = rng(fire ? 61 : 67);
    const STREAKS = [0.3, 0.48, 0.62, 0.78].map((q) => [q, 0.15 + r() * 0.25, 0.55 + r() * 0.4]);
    const SHARDS = Array.from({ length: 9 }, () => [r() * 0.9, 0.02 + r() * 0.03, 3 + Math.floor(r() * 5), 0.6 + r() * 0.8]);
    const FT = Array.from({ length: 11 }, (_, k) => ({ s: 0.08 + (k / 10) * 0.88 + (r() - 0.5) * 0.04, h: 0.16 + r() * 0.2, bend: -0.3 - r() * 0.5, ph: r() * 6.28, r1: 0.05 + r() * 0.03 }));
    return (i) => {
      const H = head[i], Ts = tail[i], Tm = tmax[i], span = Math.max(1e-3, H - Ts);
      const thick = (u) => Tm * Math.pow(clamp(u, 0, 1), 1.25) * Math.pow(1 - smooth(0.68, 1, u), 0.7) * (fire ? 2.4 : 2.8);
      const angAt = (sv) => A0 - sv * SW;
      const dash = i >= 9 ? (i - 8) / 7 : 0;
      // flame tongues: rooted on the outer edge, trail back against the swing
      const tongues = fire ? FT.filter((t) => t.s > Ts + 0.02 && t.s < H - 0.03).map((t) => {
        const u = (t.s - Ts) / span, a = angAt(t.s), T0 = thick(u);
        const boil = 0.75 + 0.25 * Math.sin(i * 2.1 + t.ph), life = 1 - smooth(5, 13, i);
        const rr = R - T0 * 0.25;
        return { bx: Math.cos(a) * rr, by: Math.sin(a) * rr, ang: Math.PI / 2 - a + 0.75, h: t.h * (0.4 + 0.9 * u) * boil * life, r1: t.r1 * (0.5 + u * 0.7), bend: t.bend + 0.3 * Math.sin(i * 1.7 + t.ph) };
      }) : [];
      return (x0, y0, s) => {
        let x = x0, y = y0;
        if (fire) { x += (NA(x0 * 2.5 + i * 4.1, y0 * 2.5 + i * 1.3) - 0.5) * 0.08; y += (NB(x0 * 2.5 - i * 2.7, y0 * 2.5 + i) - 0.5) * 0.08; }
        const rad = len(x, y);
        let a = Math.atan2(y, x), sv = (A0 - a) / SW;
        const full = (2 * Math.PI) / SW;
        sv = ((sv % full) + full) % full;
        if (sv > (1 + full) / 2) sv -= full;
        const u = (sv - Ts) / span, T = thick(u);
        const dOut = rad - R, dIn = R - T - rad;
        const dAng = (sv < Ts ? (Ts - sv) : sv > H ? (sv - H) : -Math.min(sv - Ts, H - sv)) * SW * rad;
        let d = Math.max(dOut, dIn, dAng);
        let c = Math.max(dOut + 0.004, R - T * 0.36 - rad, dAng + 0.01, (0.18 - u) * 0.4);
        // echo arc + smear line (first frames only)
        if (i >= 1 && i <= 5) {
          const e = 1 - (i - 1) / 5, Re = R * (fire ? 0.78 : 0.8), Te = 0.03 * e * Math.pow(clamp(u, 0, 1), 1.2);
          d = Math.min(d, Math.max(rad - Re, Re - Te - rad, dAng + (u < 0.3 ? (0.3 - u) * 0.5 : 0)));
        }
        if (!fire && i >= 1 && i <= 3) {
          const Rl = R * 1.07, Tl = 0.012 * Math.pow(clamp((u - 0.45) / 0.55, 0, 1), 0.5);
          d = Math.min(d, Math.max(rad - Rl, Rl - Tl - rad, dAng));
        }
        // shards peel off the receding tail
        for (const [sk, sz, birth, sp] of SHARDS) {
          if (i < birth || sk > Ts + 0.08) continue;
          const age = i - birth, life = 1 - age / 8;
          if (life <= 0) continue;
          const sa = angAt(sk), rr = R - 0.03 + age * 0.03 * sp;
          d = Math.min(d, tongue(x, y, Math.cos(sa) * rr, Math.sin(sa) * rr, -sa + Math.PI, sz * 7 * life, sz * 0.55 * life, 0, 0, 0));
        }
        for (const t of tongues) {
          if (t.h < 0.02) continue;
          d = smin(d, tongue(x, y, t.bx, t.by, t.ang, t.h, t.r1, 0, t.bend, 0.06), 0.05);
          c = Math.min(c, tongue(x, y, t.bx, t.by, t.ang, t.h * 0.45, t.r1 * 0.35, 0, t.bend, 0));
        }
        // dissolve into dashes along the arc
        if (dash > 0) d = Math.max(d, (dash * 0.9 - (0.5 + 0.5 * Math.sin(sv * 46 + Math.sin(sv * 13) * 2))) * 0.05);
        if (fire && i >= 7) d = Math.max(d, ((i - 7) / 8 * 0.8 - fbm(NC, x0 * 3, y0 * 3 - i * 0.15)) * 0.4);
        s.d = d; s.c = c;
        let k = 9;
        if (u > 0 && u < 1 && i <= 11) for (const [q, u0, u1] of STREAKS) if (u > u0 && u < u1) k = Math.min(k, Math.abs(rad - (R - T * q)) - 0.0055);
        if (fire && i >= 2 && i <= 9) k = Math.min(k, Math.max(Math.abs(fbm(ND, x * 3, y * 3 - i * 0.3) - 0.5) - 0.012, d + 0.06));
        s.k = Math.max(k, -c + 0.01);
      };
    };
  }

  // ---------- single-layer white sprites ----------
  function streakMask(w, head) {
    return (i) => (x, y, s) => { const t = y < 0 ? 1 + y * 0.1 : 1 - y * head; s.d = (Math.abs(x) / (w * t) + Math.abs(y) - 1) * w * 0.7; };
  }
  function glintMask(i) {
    const L = [0.45, 0.95, 0.65, 0.3][i], W = [0.07, 0.055, 0.04, 0.03][i];
    return (x, y, s) => {
      let d = circle(x, y, 0, 0, W * 1.3);
      for (let k = 0; k < 4; k++) d = Math.min(d, tongue(x, y, 0, 0, k * Math.PI / 2, L, W, 0, 0, 0));
      for (let k = 0; k < 4; k++) d = Math.min(d, tongue(x, y, 0, 0, k * Math.PI / 2 + Math.PI / 4, L * 0.38, W * 0.6, 0, 0, 0));
      s.d = d;
    };
  }
  function lickMask(i) {
    const r = rng(90 + i * 7), bend = (r() - 0.5) * 1.4, wave = (r() - 0.3) * 0.25;
    return (x, y, s) => {
      const wx = (NA(x * 2 + i * 5, y * 2) - 0.5) * 0.12;
      let d = tongue(x + wx, y, 0, -0.85, 0, 1.6, 0.3, 0, bend, wave);
      d = smin(d, tongue(x + wx, y, 0.12, -0.75, 0.5, 0.7, 0.14, 0, -bend, 0), 0.08);
      s.d = d;
    };
  }
  function ringMask(i) {
    const t = [0.085, 0.055, 0.032, 0.018][i], br = [0, 0.25, 0.45, 0.62][i];
    return (x, y, s) => {
      const a = Math.atan2(y, x), n = fbm(NA, Math.cos(a) * 2.5 + 7, Math.sin(a) * 2.5 + 3);
      s.d = Math.max(Math.abs(len(x, y) - (0.93 - t)) - t, (br - n) * 0.2);
    };
  }
  function puffMask(i) { // small eroding cel puff for dust / secondary smoke
    const f = smoke(Math.min(15, Math.round(i * 1.0)));
    return (x, y, s) => { const q = { d: 1, c: 9, k: 9 }; f(x * 1.05, y * 1.05 + 0.1, q); s.d = q.d; };
  }
  function rockMask() {
    const r = rng(31), P = [];
    for (let k = 0; k < 7; k++) { const a = (k / 7) * 6.283 + r() * 0.5, rr = 0.55 + r() * 0.3; P.push([Math.cos(a) * rr, Math.sin(a) * rr]); }
    return (x, y, s) => {
      let d = -9;
      for (let k = 0; k < P.length; k++) {
        const [ax, ay] = P[k], [bx, by] = P[(k + 1) % P.length], ex = bx - ax, ey = by - ay, l = len(ex, ey);
        d = Math.max(d, ((x - ax) * ey - (y - ay) * ex) / l * -1);
      }
      s.d = -(-d) ; // convex polygon sdf (approx)
      s.d = d;
      s.v = d > -0.09 ? 0.12 : (x * -0.6 + y * 0.8 > 0.05 ? 1 : 0.55);
    };
  }
  function scorchMask() {
    const r = rng(77), segs = [];
    const branch = (x, y, a, L, w, dep) => {
      let cx = x, cy = y;
      for (let k = 0; k < 6; k++) {
        a += (r() - 0.5) * 0.7;
        const nx = cx + Math.cos(a) * L / 6, ny = cy + Math.sin(a) * L / 6;
        segs.push([cx, cy, nx, ny, w]); cx = nx; cy = ny;
        if (dep < 2 && r() < 0.22) branch(cx, cy, a + (r() < 0.5 ? -1 : 1) * (0.5 + r() * 0.5), L * 0.45, w * 0.6, dep + 1);
      }
    };
    for (let k = 0; k < 11; k++) { const a = (k / 11) * 6.283 + r() * 0.3; branch(Math.cos(a) * 0.16, Math.sin(a) * 0.16, a, 0.68 + r() * 0.22, 0.022, 0); }
    return segs;
  }
  function segDist(x, y, s) {
    let d = 9;
    for (const [ax, ay, bx, by, w] of s) {
      const ex = bx - ax, ey = by - ay, t = clamp(((x - ax) * ex + (y - ay) * ey) / (ex * ex + ey * ey), 0, 1);
      d = Math.min(d, len(x - ax - ex * t, y - ay - ey * t) - w);
    }
    return d;
  }
  const SEGS = { v: null };
  const segs = () => SEGS.v || (SEGS.v = scorchMask());

  // shrink a drawing inside its cell (keeps the ground line), so tongues never hit the cell padding
  function fit(drawing, k, ground) {
    return (i, n) => {
      const f = drawing(i, n);
      return (x, y, s) => { f(x / k, (y - ground) / k + ground, s); s.d *= k; s.c *= k; s.k *= k; };
    };
  }

  // ---------- registry ----------
  const DEFS = {
    // layered heroes: each produces <name>_glow/_rim/_mid/_core
    fx_blast: { layered: true, grid: 4, rim: 0.045, glow: 0.18, coreInset: 0.05, frame: fit(blast, 0.8, -0.9), note: 'Ground fire blast, 16 drawings on 2s' },
    fx_smoke: { layered: true, grid: 4, rim: 0.04, glow: 0.12, coreInset: 0.05, frame: smoke, note: 'Cel smoke cloud: lobes, creases, round-hole dissolve' },
    fx_flash: { layered: true, grid: 2, rim: 0.035, glow: 0.2, coreInset: 0.04, frame: flash, note: 'Impact flash star, 4 drawings' },
    fx_slash: { layered: true, grid: 4, rim: 0.03, glow: 0.14, coreInset: 0.02, frame: slashDrawing('steel'), note: 'Steel crescent: streaks, echo arc, shards, dash-out' },
    fx_fireslash: { layered: true, grid: 4, rim: 0.035, glow: 0.18, coreInset: 0.03, frame: slashDrawing('fire'), note: 'Fire crescent: trailing tongues, boil, burn-out' },
    // single white sprites
    spark: { grid: 1, size: 256, frame: streakMask(0.15, 0.45), note: 'Spark streak (tip = velocity)' },
    speedline: { grid: 1, size: 256, frame: streakMask(0.04, 0.4), note: 'Speed line' },
    glint: { grid: 2, size: 512, frame: glintMask, note: 'Twinkle glint, 4 drawings' },
    flame_lick: { grid: 2, size: 1024, frame: lickMask, note: 'Flame tongue, 4 variants for Random boil' },
    ring: { grid: 2, size: 1024, frame: ringMask, note: 'Shockwave ring thinning and breaking' },
    puff: { grid: 4, size: 1024, frame: puffMask, note: 'Small cel puff with hole dissolve' },
    rock: { grid: 1, size: 256, frame: rockMask, note: 'Debris chip (value-shaded)' },
    scorch: { grid: 1, size: 1024, frame: () => (x, y, s) => { const n = fbm(NB, x * 3, y * 3); s.d = Math.min(len(x, y) - 0.5 - (n - 0.5) * 0.25, segDist(x, y, segs()) + 0.012); }, note: 'Scorch + cracks' },
    crack_glow: { grid: 1, size: 1024, frame: () => (x, y, s) => { s.d = Math.min(segDist(x, y, segs()) + 0.008, circle(x, y, 0, 0, 0.14 + (NB(x * 8, y * 8) - 0.5) * 0.05)); }, note: 'Molten crack lines' },
  };

  const cache = {};
  G.VFXPaint = {
    defs: DEFS,
    // returns { name: canvas } for every output of a def (4 for layered)
    build(name) {
      if (cache[name]) return cache[name];
      const d = DEFS[name];
      if (!d) throw new Error('Unknown drawing ' + name);
      if (d.layered) {
        const L = layered(d), o = {};
        for (const k of Object.keys(L)) o[`${name}_${k}`] = L[k];
        return (cache[name] = o);
      }
      return (cache[name] = { [name]: mask(d) });
    },
    // texture name -> [def name, grid]
    resolve(tex) {
      const m = tex.match(/^(.*)_(glow|rim|mid|core)$/);
      const base = m && DEFS[m[1]] && DEFS[m[1]].layered ? m[1] : tex;
      return { def: base, grid: DEFS[base].grid };
    },
  };
})(typeof window !== 'undefined' ? window : globalThis);
