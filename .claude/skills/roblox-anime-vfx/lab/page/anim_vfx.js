// VFX layer for the animated-model previewer (page/anim.html). Plays a clip's <clip>.vfx.json (written by
// scripts/god_anim.py) in sync with the baked animation, using the approved thunder textures.
//   Positions are god space (Blender Z-up, forward -Y) and are converted to three.js (Y-up): (x, y, z) -> (x, z, -y).
//   Anchors: [x, y, z] or {bone, off}. Event times are clip time before hit-stops; data.holds lists the hit-stops,
//   during which effects freeze (impact frames and shake keep running on real time), as in the Roblox runtime.
// Effect types: bolt, sprite, decal, ring, beam, arcs, light, flash, impact, shake, grade, letterbox, sky, eye.
import * as THREE from 'three';

const PALETTES = {
  thunder: { core: '#ffffff', mid: '#6fe0ff', rim: '#3a5cff', glow: '#2a1a9a' },
  gold: { core: '#fffbe8', mid: '#ffe08a', rim: '#e8b44a', glow: '#a8641a' },
  spark: { one: '#a6ecff' },
  dust: { one: '#7d86a3' },
};
const LAYERS = ['glow', 'rim', 'mid', 'core'];
const FPS = 30;

function rng(seed) {                         // mulberry32
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
function keys(k, u) {
  if (!k || !k.length) return 1;
  if (u <= k[0][0]) return k[0][1];
  for (let i = 1; i < k.length; i++) if (u <= k[i][0]) { const [a, va] = k[i - 1], [b, vb] = k[i]; return va + (vb - va) * (u - a) / Math.max(b - a, 1e-6); }
  return k[k.length - 1][1];
}
const ease = { in: (u) => u * u * u, out: (u) => 1 - (1 - u) ** 3, inout: (u) => u * u * (3 - 2 * u), lin: (u) => u };
const g2t = (p) => new THREE.Vector3(p[0], p[2], -p[1]);

export class VFX {
  constructor(scene, camera, root, texBase) {
    this.scene = scene; this.camera = camera; this.root = root; this.texBase = texBase;
    this.group = new THREE.Group(); scene.add(this.group);
    this.tex = {}; this.loader = new THREE.TextureLoader();
    this.overlay = new THREE.Group(); camera.add(this.overlay);
    this.items = []; this.data = null; this.enabled = false;
    this.softTex = this.makeSoft();
  }

  makeSoft() {                                // soft across-the-ribbon falloff for bolt glow
    const c = document.createElement('canvas'); c.width = 4; c.height = 64; const g = c.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 64);
    gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 4, 64); const t = new THREE.CanvasTexture(c); return t;
  }

  async texture(name) {
    if (!this.tex[name]) this.tex[name] = this.loader.loadAsync(`${this.texBase}/${name}.png`).then((t) => { t.encoding = THREE.sRGBEncoding; return t; });
    return this.tex[name];
  }

  async load(data) {
    this.data = data; this.enabled = true; this.ground = data.ground ?? -0.95;
    const need = new Set();
    for (const e of data.events) {
      if (e.type === 'sprite') { if (e.layered) LAYERS.forEach((l) => need.add(`${e.tex}_${l}`)); else need.add(e.tex); }
      if (e.type === 'decal') { LAYERS.forEach((l) => need.add(`${e.tex}_${l}`)); need.add('scorch_burn'); }
      if (e.type === 'ring') LAYERS.forEach((l) => need.add(`shock_ring_${l}`));
      if (e.type === 'beam') ['glow', 'mid', 'core'].forEach((l) => need.add(`${e.tex}_${l}`));
      if (e.type === 'sky') { need.add('storm_cloud'); need.add('storm_flash'); }
      if (e.type === 'eye') LAYERS.forEach((l) => need.add(`plasma_orb_${l}`));
    }
    await Promise.all([...need].map((n) => this.texture(n)));
    for (const k of Object.keys(this.tex)) this.tex[k] = await this.tex[k];
    this.build();
  }

  // ---------------------------------------------------------------- time
  auth(real) {                                 // real time -> clip time (frozen during hit-stops)
    let acc = 0;
    for (const [t0, d] of this.data.holds) { if (real < t0 + acc) break; if (real < t0 + acc + d) return { t: t0, frozen: true }; acc += d; }
    return { t: real - acc, frozen: false };
  }
  realStart(a) { let acc = 0; for (const [t0, d] of this.data.holds) if (t0 < a) acc += d; return a + acc; }

  anchor(a, out = new THREE.Vector3()) {
    if (Array.isArray(a)) return out.copy(g2t(a));
    const b = this.root.getObjectByName(a.bone);
    if (!b) return out.set(0, 0, 0);
    b.getWorldPosition(out); return out.add(g2t(a.off || [0, 0, 0]));
  }

  // ---------------------------------------------------------------- build objects
  layeredMats(prefix, palette, blend = THREE.AdditiveBlending, sprite = true) {
    const pal = PALETTES[palette] || PALETTES.thunder;
    // Outer glow and rim carry the colour with normal blending; only mid and core add light. Four additive layers
    // summed blue + cyan + white into flat white blobs (the white-out the quality bar forbids).
    return LAYERS.map((l, i) => {
      const map = this.tex[`${prefix}_${l}`].clone(); map.needsUpdate = true;
      const outer = l === 'glow' || l === 'rim';
      const b = blend === THREE.AdditiveBlending && outer ? THREE.NormalBlending : blend;
      const opts = { map, color: new THREE.Color(pal[l]), blending: b, transparent: true, depthWrite: false };
      const m = sprite ? new THREE.SpriteMaterial(opts) : new THREE.MeshBasicMaterial({ ...opts, side: THREE.DoubleSide });
      m.userData.base = { glow: 0.55, rim: 0.75, mid: 0.7, core: 0.8 }[l]; m.userData.order = i; return m;
    });
  }

  build() {
    this.group.clear(); this.overlay.clear(); this.items = [];
    const ov = (mat, z = -0.5) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat); m.position.z = z; m.renderOrder = 1000; m.frustumCulled = false; this.overlay.add(m); return m; };
    this.flashMesh = ov(new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false }));
    const inv = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, depthTest: false, depthWrite: false });
    inv.blending = THREE.CustomBlending; inv.blendEquation = THREE.AddEquation; inv.blendSrc = THREE.OneMinusDstColorFactor; inv.blendDst = THREE.ZeroFactor;
    this.invMesh = ov(inv); this.invMesh.renderOrder = 1001;
    const bar = () => ov(new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 1, depthTest: false, depthWrite: false }), -0.49);
    this.barTop = bar(); this.barBot = bar();
    for (const e of this.data.events) {
      const it = { e, objs: [] };
      if (e.type === 'sprite') {
        const mats = e.layered ? this.layeredMats(e.tex, e.palette, e.blend === 'normal' ? THREE.NormalBlending : THREE.AdditiveBlending)
          : [new THREE.SpriteMaterial({ map: (() => { const m = this.tex[e.tex].clone(); m.needsUpdate = true; return m; })(),
            color: new THREE.Color((PALETTES[e.palette] || PALETTES.spark).one || '#ffffff'),
            blending: e.blend === 'normal' ? THREE.NormalBlending : THREE.AdditiveBlending, transparent: true, depthWrite: false })];
        mats.forEach((m, i) => { m.userData.base = m.userData.base ?? 1; const s = new THREE.Sprite(m); s.renderOrder = 10 + i; it.objs.push(s); this.group.add(s); });
      } else if (e.type === 'decal' || e.type === 'ring') {
        const prefix = e.type === 'decal' ? e.tex : 'shock_ring';
        if (e.type === 'decal' && e.scorch) {
          const sm = new THREE.MeshBasicMaterial({ map: this.tex.scorch_burn, color: 0x05060c, transparent: true, depthWrite: false, opacity: 0 });
          const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), sm); m.rotation.x = -Math.PI / 2; m.renderOrder = 2; it.scorch = m; this.group.add(m);
        }
        this.layeredMats(prefix, e.palette || 'thunder', THREE.AdditiveBlending, false).forEach((mat, i) => {
          const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), mat); m.renderOrder = 3 + i; it.objs.push(m); this.group.add(m);
        });
        it.rot = rng((e.seed || 1) * 7919 + Math.round(e.t * 1000))() * Math.PI * 2;
      } else if (e.type === 'beam') {
        ['glow', 'mid', 'core'].forEach((l, i) => {
          const map = this.tex[`${e.tex}_${l}`].clone(); map.wrapS = map.wrapT = THREE.RepeatWrapping; map.needsUpdate = true;
          const geo = new THREE.CylinderGeometry(1, 1, e.height, 28, 1, true);
          const uv = geo.attributes.uv; for (let k = 0; k < uv.count; k++) { const u = uv.getX(k), v = uv.getY(k); uv.setXY(k, v * e.height / 1.5, u * 3); }
          const mat = new THREE.MeshBasicMaterial({ map, color: new THREE.Color(PALETTES.thunder[l]), blending: THREE.AdditiveBlending, transparent: true, depthWrite: false, side: THREE.DoubleSide });
          const m = new THREE.Mesh(geo, mat); m.renderOrder = 20 + i; m.userData.width = [1.6, 1.0, 0.45][i]; it.objs.push(m); this.group.add(m);
        });
      } else if (e.type === 'light') {
        const l = new THREE.PointLight(new THREE.Color(e.color), 0, e.range || 6, 2); it.objs.push(l); this.group.add(l);
      } else if (e.type === 'sky') {
        const cloud = new THREE.SpriteMaterial({ map: (() => { const m = this.tex.storm_cloud.clone(); m.needsUpdate = true; return m; })(), color: new THREE.Color('#1c2238'), transparent: true, depthWrite: false });
        const glow = new THREE.SpriteMaterial({ map: (() => { const m = this.tex.storm_flash.clone(); m.needsUpdate = true; return m; })(), color: new THREE.Color('#3a5cff'), blending: THREE.AdditiveBlending, transparent: true, depthWrite: false });
        [cloud, glow].forEach((m, i) => { const s = new THREE.Sprite(m); s.renderOrder = 1 + i; it.objs.push(s); this.group.add(s); });
      } else if (e.type === 'eye') {
        this.layeredMats('plasma_orb', 'thunder').forEach((m, i) => { const s = new THREE.Sprite(m); s.renderOrder = 4 + i; it.objs.push(s); this.group.add(s); });
      } else if (e.type === 'bolt' || e.type === 'arcs') {
        it.lines = [];                            // ribbons are rebuilt every frame
      }
      this.items.push(it);
    }
    this.boltPool = [];
  }

  // ---------------------------------------------------------------- bolts
  boltPath(seed, seg, kink, branches, L = 1) {
    // long bolts: more segments and kinks capped in absolute size (long straight runs, short sharp kinks)
    seg = Math.max(seg, Math.round(L * 3.2)); kink = Math.min(kink, 0.32 / Math.max(L, 0.01));
    // normalised zig-zag: long straight runs with 30-60 degree kinks; returns offsets along / across the A-B line
    const r = rng(seed), pts = [[0, 0, 0]];
    let f = 0, ox = 0, oy = 0;
    for (let i = 1; i < seg; i++) {
      f = i / seg + (r() - 0.5) * 0.35 / seg;
      const ang = r() * Math.PI * 2, mag = kink * (0.4 + r() * 0.8) * (r() < 0.25 ? 0.2 : 1);
      ox = ox * 0.35 + Math.cos(ang) * mag; oy = oy * 0.35 + Math.sin(ang) * mag;
      const taper = Math.sin(Math.PI * f);
      pts.push([f, ox * taper, oy * taper]);
    }
    pts.push([1, 0, 0]);
    const br = [];
    for (let b = 0; b < branches; b++) {
      const i0 = 1 + Math.floor(r() * (seg - 2)), len = Math.min(0.14, 0.6 / Math.max(L, 0.5)) * (0.4 + r() * 0.6), ang = r() * Math.PI * 2, bp = [pts[i0]];
      let [bf, bx, by] = pts[i0];
      for (let k = 1; k <= 4; k++) { bf += len / 4; const a = ang + (r() - 0.5) * 1.6; bx += Math.cos(a) * len * 0.45; by += Math.sin(a) * len * 0.45; bp.push([bf, bx, by]); }
      br.push(bp);
    }
    return { pts, br };
  }

  ribbon(points, width, color, opacity, soft, order) {
    const n = points.length; if (n < 2) return;
    const pos = new Float32Array(n * 2 * 3), uv = new Float32Array(n * 2 * 2), idx = [];
    const cam = this.camera.position, d = new THREE.Vector3(), v = new THREE.Vector3(), side = new THREE.Vector3();
    for (let i = 0; i < n; i++) {
      const p = points[i], q = points[Math.min(n - 1, i + 1)], o = points[Math.max(0, i - 1)];
      d.subVectors(q, o).normalize(); v.subVectors(cam, p).normalize(); side.crossVectors(d, v).normalize();
      const w = width * (i === 0 || i === n - 1 ? 0.6 : 1);
      pos.set([p.x + side.x * w, p.y + side.y * w, p.z + side.z * w, p.x - side.x * w, p.y - side.y * w, p.z - side.z * w], i * 6);
      uv.set([i / (n - 1), 0, i / (n - 1), 1], i * 4);
      if (i < n - 1) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); geo.setIndex(idx);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, map: soft ? this.softTex : null });
    const m = new THREE.Mesh(geo, mat); m.renderOrder = order; m.frustumCulled = false; this.group.add(m); this.boltPool.push(m);
  }

  drawBolt(A, B, path, width, u, flick, jitterSeed, palette = 'thunder') {
    const L = A.distanceTo(B), dir = new THREE.Vector3().subVectors(B, A);
    const up = Math.abs(dir.clone().normalize().y) > 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
    const px = new THREE.Vector3().crossVectors(dir, up).normalize(), py = new THREE.Vector3().crossVectors(dir, px).normalize();
    const jr = rng(jitterSeed);
    const map = (p) => A.clone().addScaledVector(dir, p[0]).addScaledVector(px, (p[1] + (jr() - 0.5) * 0.015) * L).addScaledVector(py, (p[2] + (jr() - 0.5) * 0.015) * L);
    const main = path.pts.map(map), brs = path.br.map((b) => b.map(map));
    // cooling: white-hot for the first frames, then cyan -> blue -> indigo afterglow, thinning out
    const pal = PALETTES[palette] || PALETTES.thunder;
    const hot = u < 0.18, cool = Math.min(1, u / 0.9);
    const glowC = new THREE.Color(pal.mid).lerp(new THREE.Color(pal.rim), Math.min(1, cool * 1.4)).lerp(new THREE.Color(pal.glow), Math.max(0, cool * 2 - 1));
    const fade = (1 - u) ** 1.4, wk = width * (hot ? 1.0 : 0.75 * (1 - 0.6 * cool));
    this.ribbon(main, wk * 4.5, glowC, 0.6 * fade * flick, true, 30);
    this.ribbon(main, wk * 1.7, new THREE.Color(pal.mid).lerp(new THREE.Color(pal.core), hot ? 0.35 : 0), 0.85 * fade * flick, true, 31);
    if (u < 0.55) this.ribbon(main, wk * 0.45, new THREE.Color(pal.core), Math.min(1, 1.6 * (1 - u / 0.55)) * flick, false, 32);
    for (const b of brs) { this.ribbon(b, wk * 2.2, glowC, 0.4 * fade * flick, true, 30); if (u < 0.4) this.ribbon(b, wk * 0.35, new THREE.Color(pal.core), (1 - u / 0.4) * flick, false, 32); }
  }

  // ---------------------------------------------------------------- per frame
  update(real, bgSet, hemi) {
    if (!this.data) return;
    for (const m of this.boltPool) { this.group.remove(m); m.geometry.dispose(); m.material.dispose(); }
    this.boltPool = [];
    if (!this.enabled) { this.group.visible = false; this.overlay.visible = false; return; }
    this.group.visible = true; this.overlay.visible = true;
    const { t } = this.auth(real), frame = Math.floor(real * FPS + 1e-4);
    const cam = this.camera, h = 2 * 0.5 * Math.tan(cam.fov * Math.PI / 360), w = h * cam.aspect;
    for (const m of [this.flashMesh, this.invMesh]) m.scale.set(w * 1.1, h * 1.1, 1);
    let flashA = 0, inv = false, shakeAmp = 0, lb = 0, gradeK = null;
    const tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3();
    for (const it of this.items) {
      const e = it.e, life = e.life || 0.3, u = (t - e.t) / life, on = u >= 0 && u <= 1;
      switch (e.type) {
        case 'sprite': {
          it.objs.forEach((s) => (s.visible = on)); if (!on) break;
          const p = this.anchor(e.at, tmp);
          if (e.move) { const k = Math.min(1, (t - e.t) / e.move.dur); p.lerp(this.anchor(e.move.to, tmp2), (ease[e.move.ease] || ease.lin)(k)); }
          const size = keys(e.size, u), a = keys(e.alpha, u), g = e.grid || 1, fr = Math.min(g * g - 1, Math.floor(u * g * g));
          it.objs.forEach((s) => {
            s.position.copy(p); s.scale.set(size, size, 1);
            const inner = s.material.userData.order >= 2 ? (e.inner ?? 1) : 1;          // fainter mid/core for big filled art
            s.material.opacity = a * (s.material.userData.base ?? 1) * inner; s.material.rotation = (e.rot + (e.spin || 0) * (t - e.t)) * Math.PI / 180;
            const m = s.material.map; m.repeat.set(1 / g, 1 / g); m.offset.set((fr % g) / g, 1 - (Math.floor(fr / g) + 1) / g);
          });
          break;
        }
        case 'decal': case 'ring': {
          const all = it.scorch ? [...it.objs, it.scorch] : it.objs;
          const alive = e.type === 'decal' ? u >= 0 && u <= 1 : on; all.forEach((m) => (m.visible = alive)); if (!alive) break;
          const p = this.anchor(e.at, tmp);
          if (e.type === 'decal') {
            const gr = ease.out(Math.min(1, (t - e.t) / (e.grow || 0.12))), sz = e.size * (0.2 + 0.8 * gr), fadeAll = u > 0.6 ? 1 - (u - 0.6) / 0.4 : 1;
            it.objs.forEach((m, i) => {
              m.position.set(p.x, this.ground + 0.004 + i * 0.001, p.z); m.rotation.set(-Math.PI / 2, 0, it.rot); m.scale.set(sz, sz, 1);
              const cool = [1 - u * 0.4, Math.max(0, 1 - u * 1.4), Math.max(0, 1 - u * 2.5), Math.max(0, 1 - u * 5)][i];   // glow lingers, core cools first
              m.material.opacity = cool * fadeAll * (i === 3 ? 1.2 : 0.9);
            });
            if (it.scorch) { it.scorch.position.set(p.x, this.ground + 0.002, p.z); it.scorch.rotation.set(-Math.PI / 2, 0, it.rot); it.scorch.scale.set(sz * 1.15, sz * 1.15, 1); it.scorch.material.opacity = 0.75 * fadeAll; }
          } else {
            const sz = keys(e.size, ease.out(u)), a = keys(e.alpha, u);
            it.objs.forEach((m) => {
              m.position.copy(p); m.scale.set(sz, sz, 1);
              if (e.orient === 'ground') m.rotation.set(-Math.PI / 2, 0, it.rot); else m.quaternion.copy(cam.quaternion);
              m.material.opacity = a * m.material.userData.base;
            });
          }
          break;
        }
        case 'beam': {
          it.objs.forEach((m) => (m.visible = on)); if (!on) break;
          const p = this.anchor(e.at, tmp), r = keys(e.radius, u), a = keys(e.alpha, u);
          it.objs.forEach((m, i) => {
            m.position.set(p.x, this.ground + e.height / 2, p.z); m.scale.set(r * m.userData.width, 1, r * m.userData.width);
            m.material.opacity = a * [0.45, 0.5, 0.55][i] * (0.85 + 0.15 * Math.sin(frame * 2.3 + i));
            m.material.map.offset.x = -(t - e.t) * e.speed * [0.7, 1, 1.3][i];
          });
          break;
        }
        case 'light': { const l = it.objs[0]; l.visible = on; if (!on) { l.intensity = 0; break; } l.position.copy(this.anchor(e.at, tmp)); l.intensity = 0.3 * keys(e.intensity, u) * (0.85 + 0.3 * rng(frame * 13 + 7)()); break; }
        case 'bolt': {
          if (!on) break;
          const A = this.anchor(e.from, new THREE.Vector3()), B = this.anchor(e.to, new THREE.Vector3());
          const flick = 0.75 + 0.5 * rng(frame * 31 + e.seed)();
          for (let s = 0; s < (e.strands || 1); s++) {
            if (!it.paths) it.paths = [];
            it.paths[s] = it.paths[s] || this.boltPath(e.seed * 17 + s * 101, e.seg || 9, (e.kink || 0.22) * (s ? 0.8 : 1), s ? Math.max(0, (e.branches || 0) - 1) : (e.branches || 0), A.distanceTo(B));
            this.drawBolt(A, B, it.paths[s], (e.width || 0.05) * (s ? 0.6 : 1), u, flick, frame * 7 + s + e.seed, e.palette);
          }
          break;
        }
        case 'arcs': {
          if (!on) break;
          const r = rng(e.seed * 977 + Math.floor(frame / 2) * 31);
          for (let k = 0; k < e.count; k++) {
            if (r() < 0.3) continue;
            const bone = e.bones[Math.floor(r() * e.bones.length)], c = this.anchor({ bone }, new THREE.Vector3());
            const A = c.clone().add(new THREE.Vector3((r() - 0.5), (r() - 0.5), (r() - 0.5)).multiplyScalar(e.radius * 2));
            const B = c.clone().add(new THREE.Vector3((r() - 0.5), (r() - 0.5), (r() - 0.5)).multiplyScalar(e.radius * 2.4));
            this.drawBolt(A, B, this.boltPath(Math.floor(r() * 1e6), 5, 0.3, 0, A.distanceTo(B)), e.width, 0.1 + r() * 0.3, 0.8 + r() * 0.4, frame + k);
          }
          break;
        }
        case 'sky': {
          it.objs.forEach((s) => (s.visible = on)); if (!on) break;
          const p = this.anchor(e.at, tmp), a = keys(e.alpha, u), g = 4, fr = Math.floor((t * 6) % 16);
          it.objs.forEach((s, i) => {
            s.position.copy(p); s.scale.set(e.size * (i ? 0.8 : 1), e.size * 0.6 * (i ? 0.8 : 1), 1);
            const m = s.material.map; m.repeat.set(1 / g, 1 / g); m.offset.set((fr % g) / g, 1 - (Math.floor(fr / g) + 1) / g);
            s.material.opacity = i === 0 ? a * 0.95 : a * (rng(frame * 3 + 11)() < 0.18 ? 0.45 : 0.05);
          });
          break;
        }
        case 'eye': {
          it.objs.forEach((s) => (s.visible = on)); if (!on) break;
          const p = this.anchor(e.at, tmp), op = keys(e.open, u);
          it.objs.forEach((s, i) => { s.position.copy(p); const wsc = [0.22, 0.17, 0.11, 0.05][i]; s.scale.set(e.size * wsc * Math.max(0.04, op), e.size * [0.9, 0.95, 0.9, 0.85][i], 1); s.material.opacity = Math.min(1, op * 1.5) * s.material.userData.base; const m = s.material.map; m.repeat.set(0.25, 0.25); m.offset.set(0, 0.75); });
          break;
        }
        case 'flash': { const s0 = this.realStart(e.t), k = (real - s0) / life; if (k >= 0 && k <= 1) flashA = Math.max(flashA, 0.6 * keys(e.alpha, k)); break; }
        case 'impact': { const s = this.realStart(e.t); if (real >= s && real < s + (e.frames || 2) / FPS) inv = true; break; }
        case 'shake': { const s = this.realStart(e.t), k = (real - s) / e.dur; if (k >= 0 && k <= 1) shakeAmp = Math.max(shakeAmp, e.amp * (1 - k) ** 2); break; }
        case 'letterbox': { const k0 = (t - e.t) / 0.2, k1 = (e.t1 - t) / 0.2; lb = Math.max(lb, Math.max(0, Math.min(1, k0, k1))); break; }
        case 'grade': gradeK = e.keys; break;
      }
    }
    this.flashMesh.material.opacity = flashA;
    this.invMesh.visible = false; this.invertNow = inv;     // the page inverts the captured frame (blend-mode invert came out black)
    const bh = h * 0.12 * ease.inout(lb);
    this.barTop.scale.set(w * 1.2, bh * 2, 1); this.barTop.position.set(0, h / 2, -0.49);
    this.barBot.scale.set(w * 1.2, bh * 2, 1); this.barBot.position.set(0, -h / 2, -0.49);
    this.barTop.visible = this.barBot.visible = lb > 0;
    if (shakeAmp > 0) { const r = rng(frame * 101 + 3); cam.position.add(new THREE.Vector3((r() - 0.5), (r() - 0.5), (r() - 0.5)).multiplyScalar(shakeAmp * 0.25)); }
    if (gradeK && bgSet) {
      let k = gradeK[0];
      if (t >= gradeK[gradeK.length - 1][0]) k = gradeK[gradeK.length - 1];
      else for (let i = 1; i < gradeK.length; i++) if (t <= gradeK[i][0]) { const a = gradeK[i - 1], b = gradeK[i], f = (t - a[0]) / Math.max(1e-6, b[0] - a[0]); k = [t, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, f < 0.5 ? a[3] : b[3]]; break; }
      bgSet(k[1], k[3]); if (hemi) hemi.intensity = 0.85 * (1 - 0.45 * k[1]);
    }
  }
}
