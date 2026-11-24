// Spec helpers shared by effect files.
(function (G) {
  'use strict';
  const LAYERS = ['glow', 'rim', 'mid', 'core'];
  // Per-layer defaults for a stacked hero (white flipbooks coloured by Color).
  const LAYER_DEFAULTS = {
    glow: { LightEmission: 1, LightInfluence: 0, Brightness: 1, Transparency: 0.5, ZOffset: 0 },
    rim: { LightEmission: 0, LightInfluence: 0, Brightness: 1, Transparency: 0, ZOffset: 0.05 },
    mid: { LightEmission: 0.05, LightInfluence: 0, Brightness: 1, Transparency: 0, ZOffset: 0.1 },
    core: { LightEmission: 0.35, LightInfluence: 0, Brightness: 1.6, Transparency: 0, ZOffset: 0.15 },
  };

  // stack(base, { glow: {...}, rim: {...}, mid: {...}, core: {...} })
  // base.props.Texture is the drawing name (e.g. 'fx_blast'); each layer gets `${Texture}_${layer}`.
  // All four emitters share position/rotation/part/emits and every motion property, so their
  // particles stay perfectly aligned in Roblox (lint enforces no randomness on stacked layers).
  function stack(base, per) {
    per = per || {};
    const zBase = base.props.ZOffset || 0;
    return LAYERS.filter((L) => per[L] !== null).map((L) => {
      const o = Object.assign({}, LAYER_DEFAULTS[L], base.props, per[L] || {});
      o.Texture = `${base.props.Texture}_${L}`;
      o.ZOffset = zBase + (per[L] && per[L].ZOffset !== undefined ? per[L].ZOffset : LAYER_DEFAULTS[L].ZOffset);
      return Object.assign({}, base, { name: `${base.name}_${L}`, stack: base.name, layer: L, props: o });
    });
  }

  // Stepped flicker: NumberSequence that holds a value per step (no smooth sine), max 20 keypoints.
  // values: array of per-step values (<= 10). fadeTo: optional final value at t=1.
  function steps(values, fadeTo) {
    const n = values.length, kp = [];
    for (let k = 0; k < n; k++) {
      const t0 = k / n, t1 = (k + 1) / n;
      kp.push([k === 0 ? 0 : t0 + 0.001, values[k]]);
      if (k < n - 1) kp.push([t1, values[k]]);
    }
    kp.push([1, fadeTo !== undefined ? fadeTo : values[n - 1]]);
    return kp.slice(0, 20);
  }
  // Deterministic flicker values around a base (amp = +/- range)
  function flicker(base, amp, n, seed) {
    let s = seed || 1;
    const out = [];
    for (let k = 0; k < n; k++) { s = (s * 16807) % 2147483647; out.push(Math.max(0, Math.min(1, base + ((s / 2147483647) * 2 - 1) * amp))); }
    return out;
  }

  // ---------- parts + combos ----------
  // A PART is one standalone VFX (its own layers, lights, impact frames, shakes, duration).
  // A COMBO stacks parts: each entry places a part at a time offset, world offset and scale.
  const PARTS = (G.VFX_PARTS = G.VFX_PARTS || {});
  function part(def) { PARTS[def.name] = def; def.isPart = true; return def; }
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const mul = (a, k) => a.map((v) => v * k);
  const scaleSeq = (v, k) => (typeof v === 'number' ? v * k : v.map((kp) => [kp[0], kp[1] * k, (kp[2] || 0) * k]));
  function compose(base, entries) {
    const fx = Object.assign({ layers: [], lights: [], impactFrames: [], shakes: [], beats: [], parts: [] }, base);
    let end = 0;
    for (const e of entries) {
      const P = PARTS[e.part];
      if (!P) throw new Error('Unknown part ' + e.part);
      const t = e.t || 0, at = e.at || [0, 0, 0], k = e.scale || 1, tag = e.tag || e.part;
      for (const L of P.layers) {
        const n = clone(L);
        n.name = `${tag}.${L.name}`; n.role = tag; n.from = e.part;
        if (L.stack) n.stack = `${tag}.${L.stack}`;
        n.position = add(at, mul(L.position || [0, 0, 0], k));
        if (L.part) n.part = { Size: mul(L.part.Size, k) };
        if (L.emits) n.emits = L.emits.map(([a, c]) => [Math.round((a + t) * 1e4) / 1e4, c]);
        if (L.rate) n.rate = L.rate.map(([a, b, r]) => [Math.round((a + t) * 1e4) / 1e4, Math.round((b + t) * 1e4) / 1e4, r]);
        if (k !== 1) {
          if (n.props.Size !== undefined) n.props.Size = scaleSeq(n.props.Size, k);
          if (Array.isArray(n.props.Speed)) n.props.Speed = n.props.Speed.map((v) => v * k);
          if (Array.isArray(n.props.Acceleration)) n.props.Acceleration = mul(n.props.Acceleration, k);
        }
        fx.layers.push(n);
      }
      for (const li of P.lights || []) fx.lights.push(Object.assign(clone(li), { name: `${tag}.${li.name}`, position: add(at, mul(li.position, k)), Brightness: li.Brightness.map(([a, v]) => [a + t, v]).concat(t > 0 ? [] : []), Range: li.Range * k }));
      for (const f of P.impactFrames || []) fx.impactFrames.push(Object.assign(clone(f), { t: f.t + t }));
      for (const sh of P.shakes || []) fx.shakes.push(Object.assign(clone(sh), { t: sh.t + t }));
      fx.beats.push([t, e.label || tag]);
      fx.parts.push({ part: e.part, tag, t, at, scale: k });
      end = Math.max(end, t + P.duration);
    }
    for (const li of fx.lights) if (li.Brightness[0][0] > 0) li.Brightness.unshift([0, 0]);
    fx.duration = Math.round(Math.max(end, base.duration || 0) * 100) / 100;
    return fx;
  }

  G.VFXSpec = { stack, steps, flicker, LAYERS, part, compose, PARTS };
})(typeof window !== 'undefined' ? window : globalThis);
