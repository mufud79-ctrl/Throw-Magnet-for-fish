// Procedural anime-style VFX textures (cel-shaded, hard-edged, ink rims).
// The same generators feed the browser viewport AND the PNG export for Roblox upload,
// so what you see in the viewer is exactly what gets uploaded as a Decal/Texture.
(function (G) {
  'use strict';

  // ---------- helpers ----------
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
  function fbm(n, x, y, o) {
    let s = 0, a = 0.5, f = 1, t = 0;
    for (let i = 0; i < (o || 4); i++) { s += a * n(x * f, y * f); t += a; a *= 0.5; f *= 2.03; }
    return s / t;
  }
  const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
  // anti-aliased hard step: the whole "cel" look lives in this function
  const aa = (x, edge, w) => clamp((x - edge) / w + 0.5, 0, 1);
  const hex = (h) => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
  const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  function bands(h, list, w) {
    let c = list[0][1];
    for (let k = 1; k < list.length; k++) c = mix(c, list[k][1], aa(h, list[k][0], w));
    return c;
  }

  // ---------- palettes (anime fire: hard 4-tone ramp + crimson ink rim) ----------
  const FLAME = [
    [-9, hex('#c81e0a')],
    [0.16, hex('#ff5a0a')],
    [0.38, hex('#ffa51e')],
    [0.6, hex('#ffe45a')],
    [0.8, hex('#fffbe8')],
  ];
  const INK = hex('#3d0604');

  // ---------- canvas builders ----------
  function canvas(size) {
    const c = typeof document !== 'undefined' ? document.createElement('canvas') : null;
    c.width = c.height = size;
    return c;
  }
  function pix(size, fn) {
    return flip(size, 1, 1, (u, v, f, i, o) => fn(u, v, o));
  }
  // flipbook: fn(u,v,frame01,frameIndex,out[r,g,b,a]) per cell; Roblox reads frames L->R, T->B
  function flip(size, cols, rows, fn) {
    const c = canvas(size), ctx = c.getContext('2d');
    const img = ctx.createImageData(size, size), d = img.data, out = [0, 0, 0, 0];
    const cw = size / cols, ch = size / rows, n = cols * rows;
    for (let y = 0; y < size; y++) {
      const row = Math.floor(y / ch), v = (y - row * ch + 0.5) / ch;
      for (let x = 0; x < size; x++) {
        const col = Math.floor(x / cw), u = (x - col * cw + 0.5) / cw;
        const idx = row * cols + col;
        out[0] = out[1] = out[2] = out[3] = 0;
        fn(u, v, n > 1 ? idx / (n - 1) : 0, idx, out);
        const i = (y * size + x) * 4;
        d[i] = out[0] * 255; d[i + 1] = out[1] * 255; d[i + 2] = out[2] * 255; d[i + 3] = out[3] * 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return c;
  }

  // ---------- generators ----------
  const N1 = Noise(11), N2 = Noise(23), N3 = Noise(37), N4 = Noise(41);

  // Cel fire puff that erodes over 16 frames (use FlipbookMode OneShot)
  function flamePuff() {
    return flip(1024, 4, 4, (u, v, f, i, o) => {
      const px = (u - 0.5) * 2, py = (v - 0.5) * 2, d = Math.hypot(px, py);
      const n1 = fbm(N1, px * 1.5 + 3.1, py * 1.5 + 1.7, 4), n2 = fbm(N2, px * 4.2 + 11, py * 4.2 + 5, 3);
      const base = 1 - d / (0.8 + f * 0.08) + (n1 - 0.5) * 1.0 + (n2 - 0.5) * 0.32 - py * 0.08;
      const cut = fbm(N3, px * 3.2 + 20, py * 3.2 + 9, 3) + (n2 - 0.5) * 0.25;
      const vis = Math.min(base, (cut - (f * 1.05 - 0.12)) * 4);
      const a = aa(vis, 0, 0.035);
      if (a <= 0) return;
      const heat = (1 - d / 0.85) * 1.0 + (n1 - 0.5) * 0.6 - py * 0.18 - f * 0.5 + 0.12;
      let c = bands(heat, FLAME, 0.02);
      c = mix(INK, c, aa(vis, 0.1, 0.03));
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }

  // Flame tongue / lick, tip at top. 2x2 variants -> FlipbookMode Random @12-15fps = anime "boil"
  function spike(palette, ink, jag, seedOff) {
    return flip(1024, 2, 2, (u, v, f, idx, o) => {
      const s = idx * 7.3 + seedOff;
      const x = (u - 0.5) * 2, y = 1 - v; // y: 0 bottom -> 1 tip
      const curve = Math.sin(y * 5.5 + s) * 0.13 * y + Math.sin(y * 11 + s * 2) * 0.03;
      const xx = x - curve;
      const w = 0.4 * Math.pow(clamp(1 - y, 0, 1), 0.9) * Math.pow(clamp(y / 0.2, 0, 1), 0.55) + 1e-4;
      const n = fbm(N4, xx * 3 + s, y * 4 - s, 3);
      const base = 1 - Math.abs(xx) / w + (n - 0.5) * jag;
      const a = aa(base, 0, 0.06);
      if (a <= 0 || y < 0.01) return;
      const heat = base * 0.9 + (1 - y) * 0.25 - 0.05 + (n - 0.5) * 0.3;
      let c = bands(heat, palette, 0.04);
      if (ink) c = mix(ink, c, aa(base, 0.16, 0.06));
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }
  const INKPAL = [[-9, hex('#0c0101')], [0.45, hex('#3a0505')], [0.8, hex('#6e0d06')]];

  // Cel smoke cluster (greyscale tones; tint with ColorSequence), erodes over 16 frames
  function smokePuff() {
    const r = rng(5), blobs = [];
    for (let i = 0; i < 7; i++) {
      const a = r() * 6.283, rad = i === 0 ? 0 : 0.22 + r() * 0.2;
      blobs.push([Math.cos(a) * rad, Math.sin(a) * rad * 0.85 - 0.04, 0.38 + r() * 0.16]);
    }
    const L = [-0.45, -0.7, 0.55], ll = Math.hypot(...L); L[0] /= ll; L[1] /= ll; L[2] /= ll;
    return flip(1024, 4, 4, (u, v, f, i, o) => {
      const px = (u - 0.5) * 2, py = (v - 0.5) * 2, k = 0.82 + f * 0.22;
      let best = -9, bn = null;
      for (const b of blobs) {
        const dx = (px - b[0] * k) / (b[2] * k), dy = (py - b[1] * k) / (b[2] * k), dd = Math.hypot(dx, dy);
        const val = 1 - dd;
        if (val > best) { best = val; bn = [dx, dy, dd]; }
      }
      const n = fbm(N2, px * 3 + 2, py * 3 + 8, 3);
      const base = best + (n - 0.5) * 0.35;
      const cut = fbm(N3, px * 3.4 + 4, py * 3.4 + 1, 3) + (n - 0.5) * 0.25;
      const vis = Math.min(base, (cut - (f * 1.05 - 0.12)) * 4);
      const a = aa(vis, 0, 0.05);
      if (a <= 0) return;
      const dd = Math.min(bn[2], 1), nz = Math.sqrt(Math.max(0, 1 - dd * dd));
      const shade = bn[0] * L[0] + bn[1] * L[1] + nz * L[2] + (n - 0.5) * 0.3;
      let t = bands(shade, [[-9, [0.4, 0.4, 0.44]], [0.12, [0.66, 0.66, 0.68]], [0.6, [1, 1, 1]]], 0.04);
      t = mix([0.14, 0.12, 0.15], t, aa(vis, 0.08, 0.04));
      o[0] = t[0]; o[1] = t[1]; o[2] = t[2]; o[3] = a;
    });
  }

  // Impact starburst (One Piece style "flash star")
  function starburst() {
    const r = rng(9), N = 14, tips = [];
    for (let i = 0; i < N; i++) tips.push([(i + (r() - 0.5) * 0.5) / N * 6.2832, 0.55 + r() * 0.45]);
    return pix(512, (u, v, o) => {
      const x = (u - 0.5) * 2, y = (v - 0.5) * 2, d = Math.hypot(x, y), th = (Math.atan2(y, x) + 6.2832) % 6.2832;
      let edge = 0.18;
      for (const [ta, L] of tips) {
        let dt = Math.abs(th - ta) % 6.2832; dt = Math.min(dt, 6.2832 - dt);
        edge = Math.max(edge, 0.18 + (L - 0.18) * Math.pow(Math.max(0, 1 - dt * N / 2.4), 2.2));
      }
      const f = 1 - d / edge;
      const a = aa(f, 0, 0.05);
      if (a <= 0) return;
      const c = bands(f, [[-9, hex('#ff8a1e')], [0.12, hex('#ffe88a')], [0.32, hex('#ffffff')]], 0.04);
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }

  // Hard-ringed glow orb (anime glow = stepped halos, not a gaussian)
  function coreGlow() {
    return pix(512, (u, v, o) => {
      const d = Math.hypot(u - 0.5, v - 0.5) * 2;
      const steps = [[1.0, hex('#ff5a12'), 0.35], [0.8, hex('#ffa53a'), 0.7], [0.6, hex('#ffe680'), 1], [0.4, hex('#ffffff'), 1]];
      let c = [0, 0, 0], a = 0;
      for (const [r, col, al] of steps) {
        const k = aa(r - d, 0, 0.012);
        if (k > 0) { c = mix(c, col, k); a = a + (al - a) * k; }
      }
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }

  // Shockwave ring (lay flat with VelocityPerpendicular), broken inner bands
  function ring() {
    return pix(1024, (u, v, o) => {
      const x = (u - 0.5) * 2, y = (v - 0.5) * 2, d = Math.hypot(x, y), th = Math.atan2(y, x);
      const n = fbm(N1, Math.cos(th) * 3 + 5, Math.sin(th) * 3 + 5, 3);
      const outer = aa(0.975 - d, 0, 0.005) * aa(d - 0.92 + (n - 0.5) * 0.03, 0, 0.005);
      const trail = aa(0.92 - d, 0, 0.005) * aa(d - 0.8 + (n - 0.5) * 0.1, 0, 0.005) * aa(n - 0.45, 0, 0.02);
      const a = Math.max(outer, trail * 0.3);
      const c = outer > 0.5 ? [1, 1, 1] : hex('#ffd98a');
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }

  // Thin diamond streaks (sparks, speed lines). Tip at the top = velocity direction.
  function streak(width, size, core) {
    return pix(size, (u, v, o) => {
      const x = (u - 0.5) * 2, y = (v - 0.5) * 2;
      const taper = y < 0 ? 1 + y * 0.15 : 1 - y * 0.45; // fatter toward the head
      const f = 1 - (Math.abs(x) / (width * taper) + Math.abs(y));
      const a = aa(f, 0, 0.04);
      if (a <= 0) return;
      const c = mix(hex(core), [1, 1, 1], aa(f, 0.35, 0.05));
      o[0] = c[0]; o[1] = c[1]; o[2] = c[2]; o[3] = a;
    });
  }

  // Ground scorch + crack network (shared geometry so the glow lines sit inside the dark cracks)
  function crackPaths() {
    const r = rng(77), paths = [];
    const branch = (x, y, ang, len, w, depth) => {
      const pts = [[x, y]];
      let cx = x, cy = y;
      const segs = 6;
      for (let i = 0; i < segs; i++) {
        ang += (r() - 0.5) * 0.7;
        cx += Math.cos(ang) * len / segs; cy += Math.sin(ang) * len / segs;
        pts.push([cx, cy]);
        if (depth < 2 && r() < 0.22) branch(cx, cy, ang + (r() < 0.5 ? -1 : 1) * (0.5 + r() * 0.5), len * 0.45, w * 0.6, depth + 1);
      }
      paths.push({ pts, w });
    };
    const n = 11;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * 6.2832 + r() * 0.3;
      branch(Math.cos(a) * 0.08, Math.sin(a) * 0.08, a, 0.34 + r() * 0.12, 1, 0);
    }
    return paths;
  }
  function strokePaths(ctx, paths, S, width, color) {
    ctx.strokeStyle = color; ctx.lineJoin = 'miter'; ctx.lineCap = 'round';
    for (const p of paths) {
      ctx.lineWidth = width * p.w;
      ctx.beginPath();
      p.pts.forEach(([x, y], i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, S / 2 + x * S, S / 2 + y * S));
      ctx.stroke();
    }
  }
  function jagged(ctx, S, rad, seed, color) {
    const r = rng(seed); ctx.fillStyle = color; ctx.beginPath();
    for (let i = 0; i <= 40; i++) {
      const a = (i / 40) * 6.2832, rr = rad * (0.82 + r() * 0.25);
      const x = S / 2 + Math.cos(a) * rr * S, y = S / 2 + Math.sin(a) * rr * S;
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    ctx.fill();
  }
  function scorch() {
    const S = 1024, c = canvas(S), ctx = c.getContext('2d'), paths = crackPaths();
    jagged(ctx, S, 0.42, 3, 'rgba(26,18,20,0.55)');
    jagged(ctx, S, 0.3, 4, 'rgba(18,12,14,0.85)');
    jagged(ctx, S, 0.14, 6, 'rgba(8,5,6,0.95)');
    strokePaths(ctx, paths, S, 16, '#060304');
    return c;
  }
  function crackGlow() {
    const S = 1024, c = canvas(S), ctx = c.getContext('2d'), paths = crackPaths();
    strokePaths(ctx, paths, S, 9, '#ff6a12');
    strokePaths(ctx, paths, S, 3.5, '#fff2b8');
    jagged(ctx, S, 0.07, 6, '#ff8a1e');
    jagged(ctx, S, 0.045, 8, '#fff2b8');
    return c;
  }

  // Debris rock chip (lit by LightInfluence in-engine)
  function rock() {
    const S = 256, c = canvas(S), ctx = c.getContext('2d'), r = rng(31), pts = [];
    for (let i = 0; i < 7; i++) { const a = (i / 7) * 6.2832 + r() * 0.5, rr = 0.3 + r() * 0.15; pts.push([S / 2 + Math.cos(a) * rr * S, S / 2 + Math.sin(a) * rr * S]); }
    const poly = (p, fill) => { ctx.fillStyle = fill; ctx.beginPath(); p.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill(); };
    ctx.lineJoin = 'round'; ctx.strokeStyle = '#0a0707'; ctx.lineWidth = 18;
    ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.stroke();
    poly(pts, '#3b2f2e');
    poly([pts[3], pts[4], pts[5], pts[6], [S * 0.52, S * 0.47]], '#665049');
    return c;
  }

  const DEFS = {
    flame_puff: { build: flamePuff, grid: [4, 4], note: 'Cel fire puff, erodes over 16 frames' },
    flame_spike: { build: () => spike(FLAME, INK, 0.5, 0), grid: [2, 2], note: 'Flame tongue, 4 variants' },
    ink_spike: { build: () => spike(INKPAL, null, 0.9, 3), grid: [2, 2], note: 'Dark crimson ink tongue (backing layer)' },
    smoke_puff: { build: smokePuff, grid: [4, 4], note: 'Cel smoke cluster, greyscale, erodes over 16 frames' },
    starburst: { build: starburst, grid: [1, 1], note: 'Impact flash star' },
    core_glow: { build: coreGlow, grid: [1, 1], note: 'Stepped-halo glow orb' },
    ring: { build: ring, grid: [1, 1], note: 'Shockwave ring' },
    spark: { build: () => streak(0.16, 256, '#ffd23c'), grid: [1, 1], note: 'Ember streak' },
    speedline: { build: () => streak(0.05, 256, '#ffe9b0'), grid: [1, 1], note: 'Impact / gather line' },
    scorch: { build: scorch, grid: [1, 1], note: 'Ground scorch + cracks' },
    crack_glow: { build: crackGlow, grid: [1, 1], note: 'Molten crack lines' },
    rock: { build: rock, grid: [1, 1], note: 'Debris chip' },
  };
  const cache = {};
  G.VFXTex = {
    defs: DEFS,
    get(name) {
      if (!DEFS[name]) throw new Error('Unknown texture ' + name);
      return cache[name] || (cache[name] = DEFS[name].build());
    },
    grid: (name) => DEFS[name].grid,
  };
})(typeof window !== 'undefined' ? window : globalThis);
