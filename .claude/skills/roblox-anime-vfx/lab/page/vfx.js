// Headless Roblox VFX emulator (three.js). Plays the same effect JSON the Luau runtime plays.
// Coordinates are Roblox studs: Y up, the caster stands at the origin facing -Z.
//
// Layer types: emitter (ParticleEmitter), shell (Part + SpecialMesh FileMesh), beam (Beam),
// bolt (neon zig-zag parts), trail (Trail ribbon), vbeam (volumetric beam: cylinder core + crossed Beams). Effect tracks: lights (PointLight), debris (crater slabs / flung rocks),
// shakes (camera), grade (ColorCorrection keys), impact (impact frames).
// Fidelity: particle maths follow Roblox semantics (sequences + envelopes, NumberRange, Speed/Spread,
// Acceleration, Drag, Rotation, flipbooks, Orientation modes, LightEmission blend, ZOffset,
// LockedToPart). Bloom/ColorCorrection/Neon are close approximations of Roblox's look.
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

const DEG = Math.PI / 180;
const W = 640, H = 360;

// ---------------------------------------------------------------- utils
function rng(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hex = (h) => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
function evalNum(seq, t, r = 0) {
  if (typeof seq === 'number') return seq;
  if (t <= seq[0][0]) return seq[0][1] + (seq[0][2] || 0) * r;
  for (let i = 1; i < seq.length; i++) {
    const b = seq[i];
    if (t <= b[0]) {
      const a = seq[i - 1], k = (t - a[0]) / (b[0] - a[0] || 1);
      return a[1] + (b[1] - a[1]) * k + ((a[2] || 0) + ((b[2] || 0) - (a[2] || 0)) * k) * r;
    }
  }
  const l = seq[seq.length - 1];
  return l[1] + (l[2] || 0) * r;
}
function evalCol(seq, t) {
  if (typeof seq === 'string') return hex(seq);
  if (!seq._c) seq._c = seq.map((k) => hex(k[1]));
  if (t <= seq[0][0]) return seq._c[0];
  for (let i = 1; i < seq.length; i++) if (t <= seq[i][0]) {
    const k = (t - seq[i - 1][0]) / (seq[i][0] - seq[i - 1][0] || 1), a = seq._c[i - 1], b = seq._c[i];
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
  }
  return seq._c[seq._c.length - 1];
}
const ease = (k, e) => e === 'out' ? 1 - (1 - k) * (1 - k) : e === 'in' ? k * k : e === 'outExpo' ? (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k)) : e === 'outBack' ? 1 + 2.7 * Math.pow(k - 1, 3) + 1.7 * Math.pow(k - 1, 2) : k;
// keys: number | [x,y,z] | [[k, value, ease?], ...]
function evalKeys(keys, k, dflt) {
  if (keys === undefined) return dflt;
  if (!Array.isArray(keys) || !Array.isArray(keys[0])) return keys;
  if (k <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (k <= keys[i][0]) {
    const a = keys[i - 1], b = keys[i], t = ease((k - a[0]) / (b[0] - a[0] || 1), b[2]);
    return Array.isArray(a[1]) ? a[1].map((v, j) => v + (b[1][j] - v) * t) : a[1] + (b[1] - a[1]) * t;
  }
  return keys[keys.length - 1][1];
}
const range = (v, r) => (typeof v === 'number' ? v : v[0] + (v[1] - v[0]) * r());
function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function norm(v, fb) { const l = Math.hypot(v[0], v[1], v[2]); return l < 1e-6 ? fb : [v[0] / l, v[1] / l, v[2] / l]; }
function rot2(a, b, t, which) {
  const c = Math.cos(t), s = Math.sin(t);
  return which === 0 ? [a[0] * c + b[0] * s, a[1] * c + b[1] * s, a[2] * c + b[2] * s] : [-a[0] * s + b[0] * c, -a[1] * s + b[1] * c, -a[2] * s + b[2] * c];
}
function hash(x) { x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); return (x ^ (x >>> 16)) >>> 0; }
const quatOf = (R) => new THREE.Quaternion().setFromEuler(new THREE.Euler((R || [0, 0, 0])[0] * DEG, (R || [0, 0, 0])[1] * DEG, (R || [0, 0, 0])[2] * DEG, 'XYZ'));
// position of a moving attachment at absolute effect time t:
//   path  [[t, [x,y,z], ease?], ...]  polyline keyed on absolute time (zig-zags, multi-leg routes), or
//   move  {from, to, t0, t1, ease, arc}  one eased leg with a vertical arc,
//   wave  {amp, freq, axis, phase, t0}  adds axis * amp * sin(2*pi*freq*(t - t0) + phase deg); amp may be
//         keys on absolute time (S-curves that tighten or die out).
function attachPos(L, t) {
  const at = L.at || [0, 0, 0];
  let p;
  if (L.path) p = evalKeys(L.path, t, at);
  else if (!L.move) p = at;
  else {
    const m = L.move, k = Math.max(0, Math.min(1, (t - m.t0) / ((m.t1 - m.t0) || 1)));
    const e = ease(k, m.ease), from = m.from || at, to = m.to;
    const arc = m.arc ? Math.sin(Math.PI * e) * m.arc : 0;
    p = [from[0] + (to[0] - from[0]) * e, from[1] + (to[1] - from[1]) * e + arc, from[2] + (to[2] - from[2]) * e];
  }
  if (L.wave) {
    const w = L.wave, ax = w.axis || [1, 0, 0], amp = evalKeys(w.amp, t, 1);
    const s = amp * Math.sin(2 * Math.PI * (w.freq || 1) * (t - (w.t0 || 0)) + (w.phase || 0) * DEG);
    p = [p[0] + ax[0] * s, p[1] + ax[1] * s, p[2] + ax[2] * s];
  }
  return p;
}
// texture swapping (strip variants): textures [...] cycled every `swap` seconds of the item's age
const swapName = (L, age) => L.textures ? L.textures[Math.max(0, Math.floor(age / (L.swap || 0.05))) % L.textures.length] : L.texture;

// ---------------------------------------------------------------- textures / meshes
const texCache = {};
let ASSET_BASE = '/assets';
function texture(name, repeat) {
  if (!name) return null;
  const key = name + (repeat ? '#r' : '');
  if (texCache[key]) return texCache[key];
  const t = new THREE.TextureLoader().load(`${ASSET_BASE}/textures/${name}.png`);
  t.premultiplyAlpha = true;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 4;
  return (texCache[key] = t);
}
const meshCache = {};
async function loadMesh(name) {
  if (meshCache[name]) return meshCache[name];
  const j = await (await fetch(`${ASSET_BASE}/meshes/${name}.json`)).json();
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(j.P, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(j.N, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(j.UV, 2));
  return (meshCache[name] = g);
}
function texturesReady() {
  return Promise.all(Object.values(texCache).map((t) => new Promise((res) => {
    if (t.image && t.image.complete !== false && t.image.width) return res();
    const iv = setInterval(() => { if (t.image && t.image.width) { clearInterval(iv); res(); } }, 20);
    setTimeout(() => { clearInterval(iv); res(); }, 8000);
  })));
}

// ---------------------------------------------------------------- particle emitter
const PDEF = {
  Brightness: 1, Color: '#ffffff', LightEmission: 0, LightInfluence: 0, Orientation: 'FacingCamera',
  Size: 1, Squash: 0, Texture: null, Transparency: 0, ZOffset: 0, EmissionDirection: 'Top', Lifetime: [1, 1],
  Rotation: [0, 0], RotSpeed: [0, 0], Speed: [5, 5], SpreadAngle: [0, 0], Shape: 'Box', ShapeInOut: 'Outward',
  ShapeStyle: 'Volume', Acceleration: [0, 0, 0], Drag: 0, LockedToPart: false, FlipbookLayout: 'None',
  FlipbookMode: 'Loop', FlipbookFramerate: [1, 1], FlipbookStartRandom: false, VelocityInheritance: 0,
};
const DIRS = { Top: [0, 1, 0], Bottom: [0, -1, 0], Front: [0, 0, -1], Back: [0, 0, 1], Right: [1, 0, 0], Left: [-1, 0, 0] };
const GRID = { None: 1, Grid2x2: 2, Grid4x4: 4, Grid8x8: 8 };
const PVERT = `attribute vec4 color4; varying vec2 vUv; varying vec4 vCol;
  void main(){ vUv = uv; vCol = color4; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
const PFRAG = `uniform sampler2D map; uniform float le; uniform float bright; varying vec2 vUv; varying vec4 vCol;
  void main(){ vec4 t = texture2D(map, vUv); float a = t.a * vCol.a;
    gl_FragColor = vec4(t.rgb * vCol.rgb * bright * vCol.a, a * (1.0 - le)); }`;

class Emitter {
  constructor(L, scene, seed) {
    this.L = L; this.seed = seed;
    this.p = Object.assign({}, PDEF, L.props);
    const p = this.p;
    if (typeof p.SpreadAngle === 'number') p.SpreadAngle = [p.SpreadAngle, p.SpreadAngle];
    this.grid = GRID[p.FlipbookLayout] || 1;
    const n = this.max = L.max || 500;
    const geo = new THREE.BufferGeometry();
    this.pos = new Float32Array(n * 12); this.uv = new Float32Array(n * 8); this.col = new Float32Array(n * 16);
    const idx = new Uint32Array(n * 6);
    for (let i = 0; i < n; i++) { const v = i * 4; idx.set([v, v + 1, v + 2, v, v + 2, v + 3], i * 6); }
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('uv', new THREE.BufferAttribute(this.uv, 2).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('color4', new THREE.BufferAttribute(this.col, 4).setUsage(THREE.DynamicDrawUsage));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    this.mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: texture(p.Texture) }, le: { value: p.LightEmission }, bright: { value: p.Brightness } },
      vertexShader: PVERT, fragmentShader: PFRAG, transparent: true, depthWrite: false, depthTest: true,
      blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor, side: THREE.DoubleSide,
    });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 20 + (p.ZOffset || 0) * 4 + (L.order || 0) * 0.001;
    this.quat = quatOf(L.rot);
    scene.add(this.mesh);
    this.reset();
  }
  reset() { this.parts = []; this.r = rng(this.seed); this.acc = 0; this.uid = 0; }
  emit(n, t) { for (let i = 0; i < n && this.parts.length < this.max; i++) this.spawn(t); }
  spawn(t) {
    const p = this.p, r = this.r, S = this.L.part;
    let pos = [0, 0, 0], dir = DIRS[p.EmissionDirection] || DIRS.Top;
    if (S) {
      const io = (n) => { const s = p.ShapeInOut === 'Inward' ? -1 : p.ShapeInOut === 'InAndOut' ? (r() < 0.5 ? -1 : 1) : 1; return [n[0] * s, n[1] * s, n[2] * s]; };
      if (p.Shape === 'Sphere') {
        const cz = 1 - 2 * r(), sz = Math.sqrt(Math.max(0, 1 - cz * cz)), a = r() * 2 * Math.PI;
        const n = [Math.cos(a) * sz, cz, Math.sin(a) * sz], k = p.ShapeStyle === 'Surface' ? 1 : Math.cbrt(r());
        pos = [n[0] * S[0] / 2 * k, n[1] * S[1] / 2 * k, n[2] * S[2] / 2 * k]; dir = io(n);
      } else if (p.Shape === 'Cylinder') {
        const a = r() * 2 * Math.PI, k = p.ShapeStyle === 'Surface' ? 1 : Math.sqrt(r()), n = [Math.cos(a), 0, Math.sin(a)];
        pos = [n[0] * S[0] / 2 * k, (r() - 0.5) * S[1], n[2] * S[2] / 2 * k]; dir = io(n);
      } else if (p.Shape === 'Disc') {
        const a = r() * 2 * Math.PI, k = p.ShapeStyle === 'Surface' ? 1 : Math.sqrt(r());
        pos = [Math.cos(a) * S[0] / 2 * k, 0, Math.sin(a) * S[2] / 2 * k]; dir = io(dir);
      } else { pos = [(r() - 0.5) * S[0], (r() - 0.5) * S[1], (r() - 0.5) * S[2]]; dir = io(dir); }
    }
    if (p.SpreadAngle[0] || p.SpreadAngle[1]) {
      const ax = (r() * 2 - 1) * p.SpreadAngle[0] * DEG, ay = (r() * 2 - 1) * p.SpreadAngle[1] * DEG;
      const tt = norm(cross(dir, Math.abs(dir[1]) < 0.99 ? [0, 1, 0] : [1, 0, 0]), [1, 0, 0]), b = cross(dir, tt);
      const v = new THREE.Vector3(...dir).applyAxisAngle(new THREE.Vector3(...b), ax).applyAxisAngle(new THREE.Vector3(...tt), ay);
      dir = [v.x, v.y, v.z];
    }
    const v = new THREE.Vector3(...pos).applyQuaternion(this.quat), w = new THREE.Vector3(...dir).applyQuaternion(this.quat);
    const o = attachPos(this.L, t), sp = range(p.Speed, r), nF = this.grid * this.grid;
    const locked = p.LockedToPart;
    this.parts.push({
      id: this.uid++, lx: v.x, ly: v.y, lz: v.z, x: locked ? v.x : o[0] + v.x, y: locked ? v.y : o[1] + v.y, z: locked ? v.z : o[2] + v.z,
      vx: w.x * sp, vy: w.y * sp, vz: w.z * sp, dx: w.x, dy: w.y, dz: w.z, age: 0, life: range(p.Lifetime, r),
      rot: range(p.Rotation, r) * DEG, rs: range(p.RotSpeed, r) * DEG, es: r() * 2 - 1, et: r() * 2 - 1, eq: r() * 2 - 1,
      fps: range(p.FlipbookFramerate, r), f0: p.FlipbookStartRandom ? Math.floor(r() * nF) : 0,
    });
  }
  step(dt, t0, t1) {
    const L = this.L, p = this.p;
    for (const em of L.emits || []) if (em[0] >= t0 && em[0] < t1) this.emit(Math.round(em[1] * (window.LAB_Q || 1)), em[0]);
    for (const w of L.rate || []) if (t1 > w[0] && t0 < w[1]) {
      this.acc += w[2] * dt; const n = Math.floor(this.acc); this.acc -= n;
      for (let i = 0; i < n; i++) this.emit(1, t0 + dt * (i + 1) / (n + 1));
    }
    const ax = p.Acceleration[0], ay = p.Acceleration[1], az = p.Acceleration[2];
    const drag = p.Drag ? Math.pow(2, -p.Drag * dt) : 1;
    this.parts = this.parts.filter((q) => {
      q.age += dt;
      if (q.age >= q.life) return false;
      q.vx = (q.vx + ax * dt) * drag; q.vy = (q.vy + ay * dt) * drag; q.vz = (q.vz + az * dt) * drag;
      q.x += q.vx * dt; q.y += q.vy * dt; q.z += q.vz * dt;
      const s = Math.hypot(q.vx, q.vy, q.vz);
      if (s > 1e-4) { q.dx = q.vx / s; q.dy = q.vy / s; q.dz = q.vz / s; }
      q.rot += q.rs * dt;
      return true;
    });
  }
  draw(cam, t) {
    const p = this.p, P = this.pos, U = this.uv, C = this.col, g = this.grid, nF = g * g;
    const cp = cam.position, e = cam.matrixWorld.elements;
    const R = [e[0], e[1], e[2]], Up = [e[4], e[5], e[6]], F = [-e[8], -e[9], -e[10]];
    const o = p.LockedToPart ? attachPos(this.L, t) : [0, 0, 0];
    const parts = this.parts;
    for (const q of parts) q.depth = (q.x + o[0] - cp.x) * F[0] + (q.y + o[1] - cp.y) * F[1] + (q.z + o[2] - cp.z) * F[2];
    parts.sort((a, b) => b.depth - a.depth);
    let n = 0;
    for (const q of parts) {
      const k = q.age / q.life, size = Math.max(0, evalNum(p.Size, k, q.es)), tr = evalNum(p.Transparency, k, q.et);
      const sq = p.Squash ? evalNum(p.Squash, k, q.eq) : 0;
      const hgt = size * (sq >= 0 ? 1 + sq : 1 / (1 - sq)) / 2, wid = size * (sq >= 0 ? 1 / (1 + sq) : 1 - sq) / 2;
      const col = evalCol(p.Color, k);
      const X = q.x + o[0], Y = q.y + o[1], Z = q.z + o[2];
      let tx = cp.x - X, ty = cp.y - Y, tz = cp.z - Z; const tl = Math.hypot(tx, ty, tz) || 1; tx /= tl; ty /= tl; tz /= tl;
      let ax, ay;
      if (p.Orientation === 'VelocityParallel') { const u = [q.dx, q.dy, q.dz]; ax = norm(cross(u, [tx, ty, tz]), R); ay = u; }
      else if (p.Orientation === 'VelocityPerpendicular') {
        const nn = [q.dx, q.dy, q.dz], tt = norm(cross(nn, Math.abs(nn[1]) < 0.99 ? [0, 1, 0] : [1, 0, 0]), R), bb = cross(nn, tt);
        ax = rot2(tt, bb, q.rot, 0); ay = rot2(tt, bb, q.rot, 1);
      } else if (p.Orientation === 'FacingCameraWorldUp') { const up = [0, 1, 0], rr = norm(cross(up, [tx, ty, tz]), R); ax = rot2(rr, up, q.rot, 0); ay = rot2(rr, up, q.rot, 1); }
      else { ax = rot2(R, Up, q.rot, 0); ay = rot2(R, Up, q.rot, 1); }
      const zo = p.ZOffset || 0, cx = X + tx * zo, cy = Y + ty * zo, cz = Z + tz * zo, b = n * 12;
      for (let c = 0; c < 4; c++) {
        const sx = c === 0 || c === 3 ? -1 : 1, sy = c < 2 ? -1 : 1;
        P[b + c * 3] = cx + ax[0] * wid * sx + ay[0] * hgt * sy;
        P[b + c * 3 + 1] = cy + ax[1] * wid * sx + ay[1] * hgt * sy;
        P[b + c * 3 + 2] = cz + ax[2] * wid * sx + ay[2] * hgt * sy;
      }
      let fr = 0;
      if (nF > 1) {
        const st = Math.floor(q.age * q.fps);
        if (p.FlipbookMode === 'OneShot') fr = Math.min(nF - 1, Math.floor(k * nF));
        else if (p.FlipbookMode === 'PingPong') { const m = (q.f0 + st) % (2 * nF - 2); fr = m < nF ? m : 2 * nF - 2 - m; }
        else if (p.FlipbookMode === 'Random') fr = hash(q.id * 131 + st * 7 + this.seed) % nF;
        else fr = (q.f0 + st) % nF;
      }
      const c0 = fr % g, row = Math.floor(fr / g), u0 = c0 / g, u1 = (c0 + 1) / g, v0 = 1 - (row + 1) / g, v1 = 1 - row / g;
      U.set([u0, v0, u1, v0, u1, v1, u0, v1], n * 8);
      const al = Math.max(0, Math.min(1, 1 - tr));
      for (let c = 0; c < 4; c++) C.set([col[0], col[1], col[2], al], n * 16 + c * 4);
      if (++n >= this.max) break;
    }
    const geo = this.mesh.geometry;
    geo.setDrawRange(0, n * 6);
    geo.attributes.position.needsUpdate = geo.attributes.uv.needsUpdate = geo.attributes.color4.needsUpdate = true;
    this.mesh.visible = n > 0;
  }
}

// ---------------------------------------------------------------- mesh shell (Part + SpecialMesh)
const SVERT = `varying vec2 vUv; varying vec3 vN; varying vec3 vV;
  void main(){ vUv = uv; vec4 wp = modelMatrix * vec4(position,1.0); vN = normalize(mat3(modelMatrix) * normal);
    vV = normalize(cameraPosition - wp.xyz); gl_Position = projectionMatrix * viewMatrix * wp; }`;
// mode 0 Neon (opaque-ish glowing solid), 1 ForceField (additive fresnel shimmer), 2 Textured (painted, alpha), 3 Glass, 4 Ice (lit crystal)
const SFRAG = `uniform sampler2D map; uniform float hasMap; uniform vec3 color; uniform float alpha, mode, bright; uniform vec2 offset, tile;
  varying vec2 vUv; varying vec3 vN; varying vec3 vV;
  void main(){
    vec4 t = hasMap > 0.5 ? texture2D(map, vUv * tile + offset) : vec4(1.0);
    float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
    if (mode < 0.5) { float a = alpha * t.a; gl_FragColor = vec4(color * bright * (0.85 + 0.35 * f) * a, a); }
    else if (mode < 1.5) { vec3 c = color * bright * t.rgb * alpha * (0.25 + 1.4 * f * f); gl_FragColor = vec4(c * t.a, 0.0); }
    else if (mode < 2.5) { float a = t.a * alpha; gl_FragColor = vec4(t.rgb * color * bright * a, a * 0.85); }
    else if (mode < 3.5) { float a = alpha * (0.12 + 0.5 * f); gl_FragColor = vec4(mix(color, vec3(1.0), f * 0.35) * a, a); }
    else { vec3 l = normalize(vec3(-0.4, 0.8, 0.45)); float d = abs(dot(normalize(vN), l));
      vec3 c = color * (0.38 + 0.5 * d) + vec3(0.9, 0.97, 1.0) * pow(f, 3.0) * 0.45; float a = alpha * (0.7 + 0.25 * f); gl_FragColor = vec4(c * a, a); }
  }`;
const SMODES = { Neon: 0, ForceField: 1, Textured: 2, Glass: 3, Ice: 4 };
class Shell {
  constructor(L, scene, geo) {
    this.L = L;
    const tex = L.texture ? texture(L.texture, true) : null;
    this.mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: tex }, hasMap: { value: tex ? 1 : 0 }, color: { value: new THREE.Color() }, alpha: { value: 1 }, mode: { value: SMODES[L.material || 'Neon'] },
        bright: { value: L.brightness || 1 }, offset: { value: new THREE.Vector2() }, tile: { value: new THREE.Vector2(...(L.tile || [1, 1])) } },
      vertexShader: SVERT, fragmentShader: SFRAG, transparent: true, depthWrite: false, side: THREE.FrontSide,
      blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.frustumCulled = false; this.mesh.visible = false;
    this.mesh.renderOrder = 10 + (L.z || 0) + (L.order || 0) * 0.001;
    this.base = quatOf(L.rot);
    this.axis = new THREE.Vector3(...(L.spinAxis || [0, 1, 0])).normalize();
    scene.add(this.mesh);
  }
  draw(cam, t) {
    const L = this.L, life = L.life || 0.5, age = t - (L.t0 || 0), m = this.mesh;
    if (age < 0 || age >= life) { m.visible = false; return; }
    const k = age / life, u = this.mat.uniforms;
    const sz = evalKeys(L.scale, k, 1), sc = Array.isArray(sz) ? sz : [sz, sz, sz];
    m.scale.set(sc[0], sc[1], sc[2]);
    const P = attachPos(L, t), V = L.velocity || [0, 0, 0];
    m.position.set(P[0] + V[0] * age, P[1] + V[1] * age, P[2] + V[2] * age);
    const spin = typeof L.spin === 'number' ? L.spin * age : evalKeys(L.spin, k, 0);
    m.quaternion.copy(this.base).multiply(new THREE.Quaternion().setFromAxisAngle(this.axis, spin * DEG));
    u.alpha.value = Math.max(0, 1 - evalKeys(L.transparency, k, 0));
    const c = L.color === undefined ? [1, 1, 1] : typeof L.color === 'string' ? hex(L.color) : evalCol(L.color, k);
    u.color.value.setRGB(c[0], c[1], c[2]);
    const scr = L.scroll || [0, 0];
    u.offset.value.set(scr[0] * age, scr[1] * age);
    m.visible = true;
  }
}

// ---------------------------------------------------------------- beam
class Beam {
  constructor(L, scene) {
    this.L = L;
    const segs = this.segs = L.segments || 24;
    const geo = new THREE.BufferGeometry();
    this.pos = new Float32Array((segs + 1) * 2 * 3); this.uv = new Float32Array((segs + 1) * 2 * 2);
    const idx = [];
    for (let i = 0; i < segs; i++) { const a = i * 2; idx.push(a, a + 1, a + 3, a, a + 3, a + 2); }
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('uv', new THREE.BufferAttribute(this.uv, 2).setUsage(THREE.DynamicDrawUsage));
    geo.setIndex(idx);
    this.mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: texture(L.texture, true) }, color: { value: new THREE.Color() }, alpha: { value: 1 }, le: { value: L.lightEmission ?? 1 }, bright: { value: L.brightness || 1 } },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
      fragmentShader: `uniform sampler2D map; uniform vec3 color; uniform float alpha, le, bright; varying vec2 vUv;
        void main(){ vec4 t = texture2D(map, vUv); float a = t.a * alpha; gl_FragColor = vec4(t.rgb * color * bright * a, a * (1.0 - le)); }`,
      transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.frustumCulled = false; this.mesh.renderOrder = 30 + (L.order || 0) * 0.001;
    scene.add(this.mesh);
  }
  draw(cam, t) {
    const L = this.L, life = L.life || 1, age = t - (L.t0 || 0);
    if (age < 0 || age >= life) { this.mesh.visible = false; return; }
    const k = age / life, a = L.from, b = evalKeys(L.to, k, L.to);
    const len = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
    const reach = evalKeys(L.reach, k, 1);
    const w = evalKeys(L.width, k, 1), w0 = Array.isArray(w) ? w[0] : w, w1 = Array.isArray(w) ? w[1] : w;
    const cp = cam.position, segs = this.segs, P = this.pos, U = this.uv;
    const dir = norm([b[0] - a[0], b[1] - a[1], b[2] - a[2]], [0, 0, -1]);
    const curve = L.curve || [0, 0, 0];
    const tl = L.textureLength || 8, scroll = (L.textureSpeed || 0) * age;
    for (let i = 0; i <= segs; i++) {
      const s = (i / segs) * reach, bend = Math.sin(Math.PI * s);
      const x = a[0] + (b[0] - a[0]) * s + curve[0] * bend, y = a[1] + (b[1] - a[1]) * s + curve[1] * bend, z = a[2] + (b[2] - a[2]) * s + curve[2] * bend;
      const vc = norm([cp.x - x, cp.y - y, cp.z - z], [0, 0, 1]), side = norm(cross(dir, vc), [1, 0, 0]);
      const wd = (w0 + (w1 - w0) * s) / 2;
      P.set([x - side[0] * wd, y - side[1] * wd, z - side[2] * wd, x + side[0] * wd, y + side[1] * wd, z + side[2] * wd], i * 6);
      const u = (s * len) / tl - scroll;
      U.set([u, 0, u, 1], i * 4);
    }
    this.mesh.geometry.attributes.position.needsUpdate = this.mesh.geometry.attributes.uv.needsUpdate = true;
    const c = typeof L.color === 'string' ? hex(L.color) : evalCol(L.color, k);
    this.mat.uniforms.color.value.setRGB(c[0], c[1], c[2]);
    this.mat.uniforms.alpha.value = Math.max(0, 1 - evalKeys(L.transparency, k, 0));
    this.mesh.visible = true;
  }
}

// ---------------------------------------------------------------- ribbon trail (Trail on two attachments)
// A Roblox Trail is emitted by two attachments on a part that rides `path`/`move`/`wave`. Roblox ages trail
// points on real time, so this does too: a hit-stop stops the head (no new length) while the tail keeps fading.
// Widths: `width` studs between the attachments (along `up`, or facing the camera with faceCamera), scaled by
// `widthScale` over the point's age; `transparency`, `color` are sequences over the point's age.
// TextureMode: Stretch (whole trail = one texture), Wrap (repeats every textureLength studs from the head),
// Static (texture pinned to where the trail was laid down).
class Trail {
  constructor(L, scene, player) {
    this.L = L; this.P = player;
    const n = this.max = 400;
    const geo = new THREE.BufferGeometry();
    this.pos = new Float32Array(n * 2 * 3); this.uv = new Float32Array(n * 2 * 2); this.col = new Float32Array(n * 2 * 4);
    const idx = [];
    for (let i = 0; i < n - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 3, a, a + 3, a + 2); }
    geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('uv', new THREE.BufferAttribute(this.uv, 2).setUsage(THREE.DynamicDrawUsage));
    geo.setAttribute('color4', new THREE.BufferAttribute(this.col, 4).setUsage(THREE.DynamicDrawUsage));
    geo.setIndex(idx);
    for (const nm of L.textures || [L.texture]) texture(nm, true);
    this.mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: texture(swapName(L, 0), true) }, le: { value: L.lightEmission ?? 1 }, bright: { value: L.brightness || 1 } },
      vertexShader: PVERT, fragmentShader: PFRAG, transparent: true, depthWrite: false, side: THREE.DoubleSide,
      blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.frustumCulled = false; this.mesh.renderOrder = 28 + (L.order || 0) * 0.001;
    scene.add(this.mesh);
    // cumulative path length on effect time (for Static texture mode)
    const T = this.P.fx.duration, step = 1 / 120; this.cum = [0]; let prev = attachPos(L, 0);
    for (let i = 1; i * step <= T + step; i++) { const q = attachPos(L, i * step); this.cum.push(this.cum[i - 1] + Math.hypot(q[0] - prev[0], q[1] - prev[1], q[2] - prev[2])); prev = q; }
  }
  cumAt(te) { const f = Math.max(0, te * 120), i = Math.min(this.cum.length - 2, Math.floor(f)), k = Math.min(1, f - i); return this.cum[i] + (this.cum[i + 1] - this.cum[i]) * k; }
  draw(cam, t, real) {
    const L = this.L, P = this.P, life = L.lifetime || 0.5;
    const rt0 = P.realOf(L.t0 || 0), rt1 = P.realOf(L.t1 ?? P.fx.duration);
    const head = Math.min(real, rt1), tail = Math.max(rt0, real - life);
    if (head <= tail + 1e-4) { this.mesh.visible = false; return; }
    const pts = [], step = 1 / 60;
    for (let r = head; r > tail; r -= step) pts.push(r);
    pts.push(tail);
    if (pts.length > this.max) pts.length = this.max;
    const X = pts.map((r) => attachPos(L, P.effectTime(r)));
    const W = L.width || 2, up = norm(L.up || [0, 1, 0], [0, 1, 0]), cp = cam.position, mode = L.textureMode || 'Stretch';
    let total = 0; const dist = [0];
    for (let i = 1; i < X.length; i++) { total += Math.hypot(X[i][0] - X[i - 1][0], X[i][1] - X[i - 1][1], X[i][2] - X[i - 1][2]); dist.push(total); }
    const Pp = this.pos, U = this.uv, C = this.col, tl = L.textureLength || 6;
    for (let i = 0; i < X.length; i++) {
      const k = Math.min(1, (real - pts[i]) / life), x = X[i];
      let side;
      if (L.faceCamera) {
        const a = X[Math.max(0, i - 1)], b = X[Math.min(X.length - 1, i + 1)];
        const tg = norm([a[0] - b[0], a[1] - b[1], a[2] - b[2]], [0, 0, -1]);
        side = norm(cross(tg, [cp.x - x[0], cp.y - x[1], cp.z - x[2]]), up);
      } else side = up;
      const w = W * Math.max(0, evalNum(L.widthScale ?? 1, k)) / 2;
      Pp.set([x[0] - side[0] * w, x[1] - side[1] * w, x[2] - side[2] * w, x[0] + side[0] * w, x[1] + side[1] * w, x[2] + side[2] * w], i * 6);
      const u = mode === 'Wrap' ? dist[i] / tl : mode === 'Static' ? -this.cumAt(P.effectTime(pts[i])) / tl : (total > 0 ? dist[i] / total : 0);
      U.set([u, 0, u, 1], i * 4);
      const col = evalCol(L.color || '#ffffff', k), al = Math.max(0, Math.min(1, 1 - evalNum(L.transparency ?? 0, k)));
      C.set([col[0], col[1], col[2], al, col[0], col[1], col[2], al], i * 8);
    }
    const geo = this.mesh.geometry;
    geo.setDrawRange(0, (X.length - 1) * 6);
    geo.attributes.position.needsUpdate = geo.attributes.uv.needsUpdate = geo.attributes.color4.needsUpdate = true;
    this.mat.uniforms.map.value = texture(swapName(L, t - (L.t0 || 0)), true);
    this.mesh.visible = true;
  }
}

// ---------------------------------------------------------------- volumetric beam (core cylinder + crossed planes)
// Roblox build: a Neon/ForceField cylinder Part for the solid core (and an optional wider `sheath`), plus
// `planes.count` Beams with FaceCamera off, fanned evenly around the axis so the energy reads from every angle.
// Planes taper (width [w0, w1]), scroll (textureSpeed), twist around the axis (deg/s) and swap textures.
const CVERT = SVERT;
class VBeam {
  constructor(L, scene) {
    this.L = L; this.group = new THREE.Group(); scene.add(this.group);
    const cyl = new THREE.CylinderGeometry(1, 1, 1, 28, 1, false);
    const mk = (spec, order) => {
      if (!spec) return null;
      const mat = new THREE.ShaderMaterial({ uniforms: { map: { value: null }, hasMap: { value: 0 }, color: { value: new THREE.Color() }, alpha: { value: 1 }, mode: { value: SMODES[spec.material || 'Neon'] },
        bright: { value: spec.brightness || 1 }, offset: { value: new THREE.Vector2() }, tile: { value: new THREE.Vector2(1, 1) } },
        vertexShader: CVERT, fragmentShader: SFRAG, transparent: true, depthWrite: false,
        blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor });
      const m = new THREE.Mesh(cyl, mat); m.frustumCulled = false; m.renderOrder = order; this.group.add(m); return m;
    };
    this.core = mk(L.core, 26 + (L.order || 0) * 0.001);
    this.sheath = mk(L.sheath, 27 + (L.order || 0) * 0.001);
    // planes: one plane set or a list of sets (e.g. dark anchor + glow + hot core), each its own Beams in Roblox
    this.sets = (L.planes ? (Array.isArray(L.planes) ? L.planes : [L.planes]) : []).map((pl, j) => {
      const n = pl.count || 3, geo = new THREE.BufferGeometry();
      const set = { pl, pos: new Float32Array(n * 4 * 3), uv: new Float32Array(n * 4 * 2) };
      const idx = []; for (let i = 0; i < n; i++) { const a = i * 4; idx.push(a, a + 1, a + 2, a, a + 2, a + 3); }
      geo.setAttribute('position', new THREE.BufferAttribute(set.pos, 3).setUsage(THREE.DynamicDrawUsage));
      geo.setAttribute('uv', new THREE.BufferAttribute(set.uv, 2).setUsage(THREE.DynamicDrawUsage));
      geo.setIndex(idx);
      for (const nm of pl.textures || [pl.texture]) texture(nm, true);
      set.mat = new THREE.ShaderMaterial({
        uniforms: { map: { value: texture(swapName(pl, 0), true) }, color: { value: new THREE.Color() }, alpha: { value: 1 }, le: { value: pl.lightEmission ?? 1 }, bright: { value: pl.brightness || 1 } },
        vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
        fragmentShader: `uniform sampler2D map; uniform vec3 color; uniform float alpha, le, bright; varying vec2 vUv;
          void main(){ vec4 t = texture2D(map, vUv); float a = t.a * alpha; gl_FragColor = vec4(t.rgb * color * bright * a, a * (1.0 - le)); }`,
        transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      });
      set.mesh = new THREE.Mesh(geo, set.mat); set.mesh.frustumCulled = false; set.mesh.renderOrder = 31 + j * 0.01 + (L.order || 0) * 0.001;
      this.group.add(set.mesh);
      return set;
    });
  }
  draw(cam, t) {
    const L = this.L, life = L.life || 1, age = t - (L.t0 || 0);
    if (age < 0 || age >= life) { this.group.visible = false; return; }
    this.group.visible = true;
    const k = age / life, a = evalKeys(L.from, k, [0, 0, 0]), bFull = evalKeys(L.to, k, L.to), reach = evalKeys(L.reach, k, 1);
    const b = [a[0] + (bFull[0] - a[0]) * reach, a[1] + (bFull[1] - a[1]) * reach, a[2] + (bFull[2] - a[2]) * reach];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]), dir = norm([b[0] - a[0], b[1] - a[1], b[2] - a[2]], [0, 0, -1]);
    const mid = new THREE.Vector3((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(...dir));
    for (const [m, spec] of [[this.core, L.core], [this.sheath, L.sheath]]) {
      if (!m) continue;
      const r = evalKeys(spec.radius, k, 0.5);
      m.visible = len > 1e-3 && r > 1e-3;
      m.position.copy(mid); m.quaternion.copy(q); m.scale.set(r, len, r);
      const u = m.material.uniforms, c = typeof spec.color === 'string' ? hex(spec.color) : evalCol(spec.color || '#ffffff', k);
      u.color.value.setRGB(c[0], c[1], c[2]); u.alpha.value = Math.max(0, 1 - evalKeys(spec.transparency, k, 0));
    }
    for (const set of this.sets) {
      const pl = set.pl, n = pl.count || 3, w = evalKeys(pl.width, k, 1), w0 = Array.isArray(w) ? w[0] : w, w1 = Array.isArray(w) ? w[1] : w;
      const base = norm(cross(dir, Math.abs(dir[1]) < 0.95 ? [0, 1, 0] : [1, 0, 0]), [1, 0, 0]), b2 = cross(dir, base);
      const tw = ((pl.twist || 0) * age + (pl.angle || 0)) * DEG, tl = pl.textureLength || 8, scroll = (pl.textureSpeed || 0) * age, u1 = len / tl;
      for (let i = 0; i < n; i++) {
        const sd = rot2(base, b2, tw + (i / n) * Math.PI, 0), o = i * 12;
        set.pos.set([a[0] - sd[0] * w0 / 2, a[1] - sd[1] * w0 / 2, a[2] - sd[2] * w0 / 2, b[0] - sd[0] * w1 / 2, b[1] - sd[1] * w1 / 2, b[2] - sd[2] * w1 / 2,
          b[0] + sd[0] * w1 / 2, b[1] + sd[1] * w1 / 2, b[2] + sd[2] * w1 / 2, a[0] + sd[0] * w0 / 2, a[1] + sd[1] * w0 / 2, a[2] + sd[2] * w0 / 2], o);
        set.uv.set([-scroll, 0, u1 - scroll, 0, u1 - scroll, 1, -scroll, 1], i * 8);
      }
      const g = set.mesh.geometry; g.attributes.position.needsUpdate = g.attributes.uv.needsUpdate = true;
      const c = typeof pl.color === 'string' ? hex(pl.color) : evalCol(pl.color || '#ffffff', k);
      set.mat.uniforms.color.value.setRGB(c[0], c[1], c[2]);
      set.mat.uniforms.alpha.value = Math.max(0, 1 - evalKeys(pl.transparency, k, 0));
      set.mat.uniforms.map.value = texture(swapName(pl, age), true);
      set.mesh.visible = len > 1e-3;
    }
  }
}

// ---------------------------------------------------------------- neon bolt (zig-zag parts)
class Bolt {
  constructor(L, scene) {
    this.L = L; this.group = new THREE.Group(); scene.add(this.group);
    this.mat = new THREE.MeshBasicMaterial({ color: new THREE.Color(...hex(L.color || '#ffffff')).multiplyScalar(L.brightness || 2.2), transparent: true, depthWrite: false });
    this.core = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 2.4, 2.4), transparent: true, depthWrite: false });
    this.box = new THREE.BoxGeometry(1, 1, 1);
    this.key = -1;
  }
  build(seed) {
    const L = this.L, r = rng(seed);
    this.group.clear();
    const a = new THREE.Vector3(...L.from), b = new THREE.Vector3(...L.to), n = L.segments || 8, jit = L.jitter ?? 1.2;
    const pts = [a.clone()];
    const d = b.clone().sub(a), side = new THREE.Vector3().crossVectors(d, new THREE.Vector3(0, 1, 0.01)).normalize(), up = new THREE.Vector3().crossVectors(side, d).normalize();
    for (let i = 1; i < n; i++) pts.push(a.clone().addScaledVector(d, i / n).addScaledVector(side, (r() * 2 - 1) * jit).addScaledVector(up, (r() * 2 - 1) * jit));
    pts.push(b.clone());
    const th = L.thickness || 0.35;
    const addSeg = (p, q, t, mat) => {
      const m = new THREE.Mesh(this.box, mat), len = p.distanceTo(q);
      m.scale.set(t, t, len); m.position.copy(p).add(q).multiplyScalar(0.5); m.lookAt(q); m.renderOrder = 25; this.group.add(m);
    };
    for (let i = 0; i < pts.length - 1; i++) { addSeg(pts[i], pts[i + 1], th, this.mat); addSeg(pts[i], pts[i + 1], th * 0.4, this.core); }
    for (let i = 1; i < pts.length - 1; i++) if (r() < (L.branch ?? 0.35)) {
      const q = pts[i].clone().addScaledVector(side, (r() * 2 - 1) * jit * 2).addScaledVector(up, (r() * 2 - 1) * jit * 2).addScaledVector(d, 0.05);
      addSeg(pts[i], q, th * 0.6, this.mat);
    }
  }
  draw(cam, t) {
    const L = this.L, age = t - (L.t0 || 0), life = L.life || 0.3;
    if (age < 0 || age >= life) { this.group.visible = false; return; }
    const key = Math.floor(age / (L.flicker || 0.05));
    if (key !== this.key) { this.key = key; this.build((L.seed || 7) * 977 + key * 13); }
    const al = Math.max(0, 1 - evalKeys(L.transparency, age / life, 0));
    this.mat.opacity = al; this.core.opacity = al;
    this.group.visible = true;
  }
}

// ---------------------------------------------------------------- debris (crater slabs + flung rocks)
class Debris {
  constructor(D, scene, groundColor) {
    this.D = D; this.group = new THREE.Group(); scene.add(this.group);
    const r = rng(D.seed || 11), col = new THREE.Color(...hex(D.color || groundColor));
    const box = new THREE.BoxGeometry(1, 1, 1);
    this.items = [];
    const n = D.count || 12, R = D.radius || 6, s = D.size || 2;
    for (let i = 0; i < n; i++) {
      const mat = new THREE.MeshLambertMaterial({ color: col.clone().multiplyScalar(0.85 + r() * 0.25) });
      const m = new THREE.Mesh(box, mat); m.castShadow = true; m.receiveShadow = true;
      const a = (i / n) * Math.PI * 2 + (r() - 0.5) * 0.4;
      const it = { m, a, sz: [s * (0.7 + r() * 0.8), s * (0.25 + r() * 0.35), s * (0.6 + r() * 0.7)], r: R * (0.85 + r() * 0.3), tilt: 20 + r() * 35, spin: (r() - 0.5) * 30,
        v: [(r() - 0.5) * 2, 0, (r() - 0.5) * 2], up: (D.speed || 30) * (0.6 + r() * 0.6), out: (D.speed || 30) * 0.35 * (0.5 + r()), rs: [(r() - 0.5) * 12, (r() - 0.5) * 12, (r() - 0.5) * 12] };
      this.items.push(it); this.group.add(m);
    }
    if (D.kind === 'crater') { // dark pit disc
      this.pit = new THREE.Mesh(new THREE.CircleGeometry(1, 32), new THREE.MeshBasicMaterial({ color: new THREE.Color(...hex(D.pitColor || '#2a2420')), transparent: true }));
      this.pit.rotation.x = -Math.PI / 2; this.pit.position.y = 0.03; this.group.add(this.pit);
    }
  }
  draw(cam, t) {
    const D = this.D, age = t - D.t, life = D.life || 3, at = D.at || [0, 0, 0];
    if (age < 0 || age > life) { this.group.visible = false; return; }
    this.group.visible = true;
    const sink = Math.max(0, (age - (life - 0.6)) / 0.6);
    if (this.pit) { const k = Math.min(1, age / 0.08); this.pit.scale.setScalar((D.radius || 6) * 0.95 * k); this.pit.position.set(at[0], 0.03, at[2]); this.pit.material.opacity = 1 - sink; }
    for (const it of this.items) {
      const m = it.m;
      if (D.kind === 'crater') {
        const k = Math.min(1, age / 0.1), e = ease(k, 'outBack');
        m.scale.set(it.sz[0] * e, it.sz[1] * e, it.sz[2] * e);
        m.position.set(at[0] + Math.cos(it.a) * it.r, it.sz[1] * 0.25 - sink * 2, at[2] + Math.sin(it.a) * it.r);
        m.rotation.set(0, -it.a, 0); m.rotateZ(it.tilt * DEG); m.rotateY(it.spin * DEG);
      } else {
        const g = 70, tt = Math.min(age, 1.6);
        const y = 0.5 + it.up * tt - 0.5 * g * tt * tt;
        const k = Math.max(0, Math.min(1, 1 - (age - life + 0.5) / 0.5));
        m.scale.set(it.sz[0] * 0.45 * k, it.sz[0] * 0.45 * k, it.sz[0] * 0.45 * k);
        m.position.set(at[0] + Math.cos(it.a) * it.out * tt, Math.max(0.3, y), at[2] + Math.sin(it.a) * it.out * tt);
        m.rotation.set(it.rs[0] * tt, it.rs[1] * tt, it.rs[2] * tt);
      }
    }
  }
}

// ---------------------------------------------------------------- arena + post
const GradeShader = {
  uniforms: { tDiffuse: { value: null }, bright: { value: 0 }, contrast: { value: 0 }, sat: { value: 0 }, tint: { value: new THREE.Color(1, 1, 1) }, invert: { value: 0 }, mono: { value: 0 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float bright, contrast, sat, invert, mono; uniform vec3 tint; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; c = c + bright; c = (c - 0.5) * (1.0 + contrast) + 0.5;
      float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, 1.0 + sat); c *= tint;
      if (mono > 0.5) { float m = step(0.62, l); c = vec3(m); }
      if (invert > 0.5) c = 1.0 - clamp(c, 0.0, 1.0);
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0); }`,
};

function makeArena(scene) {
  const sky = document.createElement('canvas'); sky.width = 4; sky.height = 256;
  const g = sky.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, '#3b7de0'); gr.addColorStop(0.62, '#8fc0f2'); gr.addColorStop(1, '#cfe4f7');
  g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
  scene.background = new THREE.CanvasTexture(sky);
  scene.fog = new THREE.Fog('#c3dcf3', 70, 260);
  const sand = document.createElement('canvas'); sand.width = sand.height = 512;
  const s = sand.getContext('2d'); s.fillStyle = '#dcc79d'; s.fillRect(0, 0, 512, 512);
  const rr = rng(5);
  for (let i = 0; i < 2600; i++) { s.fillStyle = `rgba(${150 + rr() * 60},${125 + rr() * 50},${85 + rr() * 40},${0.05 + rr() * 0.08})`; s.fillRect(rr() * 512, rr() * 512, 2 + rr() * 6, 1 + rr() * 3); }
  s.strokeStyle = 'rgba(160,135,95,0.18)'; s.lineWidth = 2;
  for (let i = 0; i < 9; i++) { s.beginPath(); const y = rr() * 512; s.moveTo(0, y); s.bezierCurveTo(170, y + 30 * (rr() - 0.5), 340, y + 30 * (rr() - 0.5), 512, y); s.stroke(); }
  const st = new THREE.CanvasTexture(sand); st.wrapS = st.wrapT = THREE.RepeatWrapping; st.repeat.set(24, 24);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), new THREE.MeshLambertMaterial({ map: st }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  scene.add(new THREE.HemisphereLight('#cfe6ff', '#9c8660', 0.55));
  const sun = new THREE.DirectionalLight('#fff4e0', 0.5); sun.position.set(-30, 60, 25); sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -30, right: 30, top: 30, bottom: -30 });
  scene.add(sun);
  return '#dcc79d';
}

// Blocky R15-ish rig: root (feet) > upper body (pivot at the hips) > arms (pivot at the shoulders).
// Pose keys animate it so anticipation / follow-through read on the caster, and hit reactions on dummies.
function makeAvatar(scene, at, yaw, shirt = '#22283a') {
  const root = new THREE.Group(), upper = new THREE.Group(), armR = new THREE.Group(), armL = new THREE.Group();
  const box = (grp, w, h, d, x, y, z, c) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshLambertMaterial({ color: c })); m.position.set(x, y, z); m.castShadow = true; grp.add(m); return m; };
  box(root, 1, 2, 1, -0.5, 1, 0, '#2f3446'); box(root, 1, 2, 1, 0.5, 1, 0, '#2f3446');
  upper.position.set(0, 2, 0); root.add(upper);
  box(upper, 2, 2, 1, 0, 1, 0, shirt);
  box(upper, 1.15, 1.15, 1.15, 0, 2.6, 0, '#e8c39e'); box(upper, 1.25, 0.35, 1.25, 0, 3.2, 0, '#1b1b22');
  armR.position.set(1.5, 1.9, 0); upper.add(armR); box(armR, 1, 2, 1, 0, -0.9, 0, shirt);
  armL.position.set(-1.5, 1.9, 0); upper.add(armL); box(armL, 1, 2, 1, 0, -0.9, 0, shirt);
  root.position.set(...at); root.rotation.y = yaw; scene.add(root);
  return { root, upper, armR, armL, at: at.slice(), yaw };
}
function poseAvatar(rig, P, t) {
  if (!P) return;
  const D = DEG;
  rig.upper.rotation.set(evalKeys(P.lean, t, 0) * D, evalKeys(P.twist, t, 0) * D, 0);
  rig.armR.rotation.set(evalKeys(P.armR, t, 0) * D, 0, evalKeys(P.armRz, t, 0) * D);
  rig.armL.rotation.set(evalKeys(P.armL, t, 0) * D, 0, evalKeys(P.armLz, t, 0) * D);
  const off = evalKeys(P.offset, t, [0, 0, 0]);
  rig.root.position.set(rig.at[0] + off[0], rig.at[1] + off[1], rig.at[2] + off[2]);
  const sq = evalKeys(P.scale, t, [1, 1, 1]);
  rig.root.scale.set(sq[0], sq[1], sq[2]);
}
// Hit reaction (squash & stretch + knockback): squash flat on contact, stretch up, settle; slide back with a tilt.
function hitPose(h) {
  const t = h.t, k = h.power || 1, dir = h.dir || [0, 0, -1], d = 3.5 * k;
  return {
    scale: [[t - 0.001, [1, 1, 1]], [t + 0.05, [1 + 0.3 * k, 1 - 0.32 * k, 1 + 0.3 * k], 'out'], [t + 0.16, [1 - 0.12 * k, 1 + 0.18 * k, 1 - 0.12 * k]], [t + 0.32, [1, 1, 1]]],
    offset: [[t - 0.001, [0, 0, 0]], [t + 0.3, [dir[0] * d, 0, dir[2] * d], 'out'], [t + 0.7, [dir[0] * d * 1.1, 0, dir[2] * d * 1.1], 'out']],
    lean: [[t - 0.001, 0], [t + 0.08, -28 * k, 'out'], [t + 0.5, -8 * k], [t + 0.9, 0]],
  };
}

// Afterimage: a flat-colour clone of the caster left behind on a dash, fading and drifting back.
class Ghost {
  constructor(G, scene) {
    this.G = G;
    this.rig = makeAvatar(scene, G.at, 0);
    this.mats = [];
    this.rig.root.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.material = new THREE.MeshBasicMaterial({ color: new THREE.Color(...hex(G.color || '#ffffff')).multiplyScalar(1.4), transparent: true, depthWrite: false }); o.renderOrder = 15; this.mats.push(o.material); } });
    this.rig.upper.rotation.x = (G.lean || -30) * DEG;
  }
  draw(cam, t) {
    const G = this.G, age = t - G.t, life = G.life || 0.35;
    this.rig.root.visible = age >= 0 && age < life;
    if (!this.rig.root.visible) return;
    const k = age / life;
    for (const m of this.mats) m.opacity = 0.55 * (1 - k);
    this.rig.root.position.set(G.at[0], G.at[1], G.at[2] + k * 0.8);
    this.rig.root.scale.set(1 + 0.1 * k, 1 + 0.1 * k, 1 + 0.1 * k);
  }
}

// Damage number: pops (squash -> stretch -> settle), arcs up and away, falls, fades. A canvas sprite.
class DamageNumber {
  constructor(N, scene) {
    this.N = N;
    const c = document.createElement('canvas'); c.width = 256; c.height = 128;
    const g = c.getContext('2d'); g.font = 'bold 84px Impact, "Arial Black", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = 14; g.strokeStyle = '#140a06'; g.strokeText(N.text, 128, 66);
    const gr = g.createLinearGradient(0, 30, 0, 100); gr.addColorStop(0, '#ffffff'); gr.addColorStop(1, N.color || '#ffd23a');
    g.fillStyle = gr; g.fillText(N.text, 128, 66);
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthTest: false }));
    this.sprite.renderOrder = 99; this.sprite.visible = false; scene.add(this.sprite);
  }
  draw(cam, t) {
    const N = this.N, age = t - N.t, life = N.life || 1.25;
    if (age < 0 || age > life) { this.sprite.visible = false; return; }
    const v = N.vel || [2.5, 17, 0], g = 30;
    this.sprite.position.set(N.at[0] + v[0] * age, N.at[1] + v[1] * age - 0.5 * g * age * age, N.at[2] + v[2] * age);
    const pop = evalKeys([[0, [0.2, 0.2]], [0.06, [1.5, 0.7], 'out'], [0.14, [0.85, 1.25]], [0.24, [1, 1]], [1, [1, 1]]], age, [1, 1]);
    const s = N.size || 2.6;
    this.sprite.scale.set(s * 2 * pop[0], s * pop[1], 1);
    this.sprite.material.opacity = age > life - 0.25 ? (life - age) / 0.25 : 1;
    this.sprite.visible = true;
  }
}

// ---------------------------------------------------------------- effect player
class Player {
  constructor() {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, canvas: document.getElementById('vp') });
    this.renderer.setSize(W, H, false); this.renderer.shadowMap.enabled = true;
    this.camera = new THREE.PerspectiveCamera(60, W / H, 0.3, 1000);
    this.composer = new EffectComposer(this.renderer);
    this.scene = null;
  }
  async load(fx) {
    this.fx = fx; this.stops = (fx.hitstop || []).slice().sort((x, y) => x.t - y.t);
    const scene = this.scene = new THREE.Scene();
    this.groundColor = makeArena(scene);
    this.caster = fx.caster !== false ? makeAvatar(scene, [0, 0, 0], 0) : null;
    this.dummies = (fx.dummies || []).map((d) => makeAvatar(scene, d, Math.PI, '#5a2626'));
    this.dummyPose = this.dummies.map((_, j) => {           // merge every hit on this dummy into one pose track
      const hs = (fx.hits || []).filter((h) => (h.dummy || 0) === j);
      if (!hs.length) return null;
      const P = { scale: [], offset: [], lean: [] }; let acc = [0, 0, 0];
      for (const h of hs) { const hp = hitPose(h); for (const k of ['scale', 'lean']) P[k] = P[k].concat(hp[k]);
        P.offset = P.offset.concat(hp.offset.map((kf) => [kf[0], [kf[1][0] + acc[0], 0, kf[1][2] + acc[2]]].concat(kf.slice(2))));
        const last = hp.offset[hp.offset.length - 1][1]; acc = [acc[0] + last[0], 0, acc[2] + last[2]]; }
      for (const k of Object.keys(P)) P[k].sort((x, y) => x[0] - y[0]);
      return P;
    });
    this.items = [];
    let i = 0;
    for (const L of fx.layers) {
      L.order = i++;
      if (L.type === 'emitter') this.items.push(new Emitter(L, scene, L.seed ?? (1000 + i * 7919)));
      else if (L.type === 'shell') this.items.push(new Shell(L, scene, await loadMesh(L.mesh)));
      else if (L.type === 'beam') this.items.push(new Beam(L, scene));
      else if (L.type === 'bolt') this.items.push(new Bolt(L, scene));
      else if (L.type === 'trail') this.items.push(new Trail(L, scene, this));
      else if (L.type === 'vbeam') this.items.push(new VBeam(L, scene));
    }
    for (const D of fx.debris || []) this.items.push(new Debris(D, scene, this.groundColor));
    for (const N of fx.numbers || []) this.items.push(new DamageNumber(N, scene));
    for (const G of fx.ghosts || []) this.items.push(new Ghost(G, scene));
    this.lights = (fx.lights || []).map((Lt) => { const p = new THREE.PointLight(new THREE.Color(...hex(Lt.color || '#ffffff')), 0, Lt.range || 16, 2); scene.add(p); return { Lt, p }; });
    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(scene, this.camera));
    this.bloom = new UnrealBloomPass(new THREE.Vector2(W, H), fx.bloom ?? 0.5, 0.45, 0.88);
    this.composer.addPass(this.bloom);
    this.grade = new ShaderPass(GradeShader); this.composer.addPass(this.grade);
    await texturesReady();
    this.t = 0;
    this.stops = (fx.hitstop || []).slice().sort((x, y) => x.t - y.t);
    return fx.duration + this.stops.reduce((a, h) => a + h.dur, 0);
  }
  // Hit-stop: map real time to effect time. While a stop holds, effect time is frozen (particles, shells,
  // poses, flipbooks); camera shake keeps running on real time, like a game freezing its simulation.
  effectTime(real) {
    let te = real, shift = 0;
    for (const h of this.stops) {
      const start = h.t + shift;
      if (real <= start) break;
      te = real - shift - Math.min(real - start, h.dur);
      if (real < start + h.dur) return h.t;
      shift += h.dur;
      te = real - shift;
    }
    return te;
  }
  realOf(te) { return te + this.stops.filter((h) => h.t < te - 1e-6).reduce((a, h) => a + h.dur, 0); }
  // advance to time t (monotonic) and render
  frame(real) {
    const t = this.effectTime(real);
    const dt = 1 / 60;
    while (this.t < t - 1e-9) {
      const t0 = this.t, t1 = Math.min(t, t0 + dt);
      for (const it of this.items) if (it instanceof Emitter) it.step(t1 - t0, t0, t1);
      this.t = t1;
    }
    const fx = this.fx, cam = this.camera, C = fx.camera || {};
    const cpos = evalKeys(C.pos, Math.min(1, t / fx.duration), [14, 9, 16]), look = evalKeys(C.look, Math.min(1, t / fx.duration), [0, 3, -6]);
    let sh = [0, 0, 0];
    // shakes run on real time so they keep going through a hit-stop
    const shiftAt = (te) => this.stops.filter((h) => h.t < te).reduce((a, h) => a + h.dur, 0);
    for (const s of fx.shakes || []) { const st = s.t + shiftAt(s.t + 1e-6) - (this.stops.some((h) => Math.abs(h.t - s.t) < 1e-3) ? this.stops.find((h) => Math.abs(h.t - s.t) < 1e-3).dur : 0);
      if (!(real >= st && real < st + s.dur)) continue;
      const k = (real - st) / s.dur, amp = s.amp * Math.pow(1 - k, 2), w = (real - st) * (s.freq || 20);
      sh = [sh[0] + amp * Math.sin(w * 6.1 + 1.3), sh[1] + amp * Math.sin(w * 7.3 + 4.1) * 0.8, sh[2] + amp * Math.sin(w * 5.2 + 2.2) * 0.5];
    }
    cam.position.set(cpos[0] + sh[0], cpos[1] + sh[1], cpos[2] + sh[2]);
    cam.fov = evalKeys(C.fov, Math.min(1, t / fx.duration), 60); cam.updateProjectionMatrix();
    cam.lookAt(look[0] + sh[0] * 0.5, look[1] + sh[1] * 0.5, look[2]);
    cam.updateMatrixWorld();
    for (const it of this.items) it.draw(cam, t, real);
    if (this.caster) poseAvatar(this.caster, fx.pose, t);
    this.dummies.forEach((d, j) => poseAvatar(d, this.dummyPose[j], t));
    for (const { Lt, p } of this.lights) { const P = attachPos(Lt, t); p.position.set(...P); const bk = Lt.brightness; p.intensity = t < bk[0][0] ? 0 : Math.max(0, evalKeys(bk, t, 0)) * 0.12; }
    // colour grade + impact frames
    const u = this.grade.uniforms;
    let b = 0, c = 0, s = 0, tint = [1, 1, 1];
    if (fx.grade && fx.grade.length) {
      const g = fx.grade; let a = g[0], bb = g[0], k = 0;
      for (let j = 1; j < g.length; j++) { if (t <= g[j][0]) { a = g[j - 1]; bb = g[j]; k = (t - a[0]) / (bb[0] - a[0] || 1); break; } a = bb = g[j]; }
      const ta = hex(a[4] || '#ffffff'), tb = hex(bb[4] || '#ffffff'), Lr = (x, y) => x + (y - x) * k;
      b = Lr(a[1], bb[1]); c = Lr(a[2], bb[2]); s = Lr(a[3], bb[3]); tint = [Lr(ta[0], tb[0]), Lr(ta[1], tb[1]), Lr(ta[2], tb[2])];
    }
    u.invert.value = 0; u.mono.value = 0;
    // impact frames run on real time: they flash for a couple of frames at the start of a hit-stop
    const realStart = (te) => te + this.stops.filter((h) => h.t < te - 1e-6).reduce((a, h) => a + h.dur, 0);
    for (const f of fx.impact || []) if (real >= realStart(f.t) && real < realStart(f.t) + f.dur) {
      if (f.mode === 'invert') u.invert.value = 1;
      else if (f.mode === 'mono') u.mono.value = 1;
      else if (f.mode === 'white') { b = 0.35; c = 0.2; s = -0.6; }
      else if (f.mode === 'black') { b = -0.35; c = 0.6; s = -1; }
    }
    u.bright.value = b; u.contrast.value = c; u.sat.value = s; u.tint.value.setRGB(tint[0], tint[1], tint[2]);
    if (window.LAB_NOPOST === 1) this.renderer.render(this.scene, cam);
    else if (window.LAB_NOPOST === 2) { this.bloom.enabled = false; this.composer.render(); this.bloom.enabled = true; }
    else this.composer.render();
  }
}

window.LAB = {
  player: null,
  realTime(te) { const P = this.player; return te + (P.stops || []).filter((h) => h.t < te - 1e-6).reduce((a, h) => a + h.dur, 0); },
  async load(fx, base) { if (base) ASSET_BASE = base; this.player = this.player || new Player(); return this.player.load(fx); },
  frame(t) { this.player.frame(t); return document.getElementById('vp').toDataURL('image/jpeg', 0.9); },
};
window.LAB_READY = true;
