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

  G.VFXSpec = { stack, steps, flicker, LAYERS };
})(typeof window !== 'undefined' ? window : globalThis);
