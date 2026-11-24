// Headless-Roblox VFX emulator.
// Implements Roblox ParticleEmitter semantics in three.js so an effect spec written with
// Roblox property names previews here and exports 1:1 to Luau (see luau.js).
//
// Fidelity notes (also in the skill's reference/roblox-mapping.md):
//  * Exact: NumberSequence/ColorSequence eval incl. envelopes, NumberRange, Lifetime, Speed,
//    Acceleration, Rotation/RotSpeed, Flipbook (Loop/OneShot/PingPong/Random), Orientation modes,
//    LightEmission blend (0 = alpha, 1 = additive), LightInfluence, Brightness, Emit()/Rate timing.
//  * Approximate: Drag (halving-time model), Squash curve, ZOffset (moves the quad toward the camera),
//    sorting between emitters, Bloom/ColorCorrection look.
(function (G) {
  'use strict';
  const THREE = G.THREE;
  const DEG = Math.PI / 180;

  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const hex = (h) => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];

  // NumberSequence: number | [[t, value, envelope?], ...]; r in [-1, 1] picks within the envelope
  function evalNum(seq, t, r) {
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
  // ColorSequence: '#hex' | [[t, '#hex'], ...]
  function evalCol(seq, t) {
    if (typeof seq === 'string') return hex(seq);
    if (seq._c === undefined) seq._c = seq.map((k) => hex(k[1]));
    if (t <= seq[0][0]) return seq._c[0];
    for (let i = 1; i < seq.length; i++) {
      if (t <= seq[i][0]) {
        const k = (t - seq[i - 1][0]) / (seq[i][0] - seq[i - 1][0] || 1), a = seq._c[i - 1], b = seq._c[i];
        return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
      }
    }
    return seq._c[seq._c.length - 1];
  }
  const range = (v, r) => (typeof v === 'number' ? v : v[0] + (v[1] - v[0]) * r());

  // Keyframe track [[t, v], ...] with linear interpolation (lights, color correction)
  function track(keys, t) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      if (t <= keys[i][0]) {
        const a = keys[i - 1], b = keys[i], k = (t - a[0]) / (b[0] - a[0] || 1);
        return a[1] + (b[1] - a[1]) * k;
      }
    }
    return keys[keys.length - 1][1];
  }

  const DEFAULTS = {
    Brightness: 1, Color: '#ffffff', LightEmission: 0, LightInfluence: 0, Orientation: 'FacingCamera',
    Size: 1, Squash: 0, Texture: null, Transparency: 0, ZOffset: 0,
    EmissionDirection: 'Top', Lifetime: [1, 1], Rate: 0, Rotation: [0, 0], RotSpeed: [0, 0],
    Speed: [5, 5], SpreadAngle: [0, 0], Shape: 'Box', ShapeInOut: 'Outward', ShapeStyle: 'Volume',
    ShapePartial: 1, Acceleration: [0, 0, 0], Drag: 0, LockedToPart: false, TimeScale: 1,
    FlipbookLayout: 'None', FlipbookMode: 'Loop', FlipbookFramerate: [1, 1], FlipbookStartRandom: false,
  };
  const DIRS = { Top: [0, 1, 0], Bottom: [0, -1, 0], Front: [0, 0, -1], Back: [0, 0, 1], Right: [1, 0, 0], Left: [-1, 0, 0] };
  const GRID = { None: 1, Grid2x2: 2, Grid4x4: 4, Grid8x8: 8 };

  const VERT = `
    attribute vec4 color4;
    varying vec2 vUv; varying vec4 vCol;
    void main(){ vUv = uv; vCol = color4; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
  // texture is premultiplied; LightEmission lerps alpha-blend -> additive
  const FRAG = `
    uniform sampler2D map; uniform float le; uniform float bright;
    varying vec2 vUv; varying vec4 vCol;
    void main(){
      vec4 t = texture2D(map, vUv);
      float a = t.a * vCol.a;
      gl_FragColor = vec4(t.rgb * vCol.rgb * bright * vCol.a, a * (1.0 - le));
    }`;

  class Emitter {
    constructor(layer, sim, seed) {
      this.layer = layer; this.sim = sim; this.seed = seed;
      this.p = Object.assign({}, DEFAULTS, layer.props);
      const p = this.p;
      this.grid = GRID[p.FlipbookLayout] || 1;
      this.max = layer.max || 600;
      const n = this.max;
      const geo = new THREE.BufferGeometry();
      this.pos = new Float32Array(n * 12); this.uv = new Float32Array(n * 8); this.col = new Float32Array(n * 16);
      const idx = new Uint32Array(n * 6);
      for (let i = 0; i < n; i++) { const v = i * 4, k = i * 6; idx.set([v, v + 1, v + 2, v, v + 2, v + 3], k); }
      geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
      geo.setAttribute('uv', new THREE.BufferAttribute(this.uv, 2).setUsage(THREE.DynamicDrawUsage));
      geo.setAttribute('color4', new THREE.BufferAttribute(this.col, 4).setUsage(THREE.DynamicDrawUsage));
      geo.setIndex(new THREE.BufferAttribute(idx, 1));
      geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e5);
      this.mat = new THREE.ShaderMaterial({
        uniforms: { map: { value: sim.texture(p.Texture) }, le: { value: p.LightEmission }, bright: { value: p.Brightness } },
        vertexShader: VERT, fragmentShader: FRAG, transparent: true, depthWrite: false, depthTest: true,
        blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
        blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor, side: THREE.DoubleSide,
      });
      this.mesh = new THREE.Mesh(geo, this.mat);
      this.mesh.frustumCulled = false;
      this.mesh.renderOrder = 10 + (p.ZOffset || 0) * 10 + (layer.order || 0) * 0.01;
      this.origin = new THREE.Vector3().fromArray(layer.position || [0, 0, 0]);
      const R = layer.rotation || [0, 0, 0];
      this.quat = new THREE.Quaternion().setFromEuler(new THREE.Euler(R[0] * DEG, R[1] * DEG, R[2] * DEG, 'XYZ'));
      this.rotated = R.some((v) => v);
      this.partSize = layer.part ? layer.part.Size : null;
      this.reset();
    }
    reset() {
      this.parts = []; this.r = rng(this.seed); this.acc = 0; this.uid = 0;
    }
    emit(n) {
      for (let i = 0; i < n && this.parts.length < this.max; i++) this.spawn();
    }
    spawn() {
      const p = this.p, r = this.r;
      let pos = [0, 0, 0], dir = DIRS[p.EmissionDirection] || DIRS.Top, useSpread = true;
      const S = this.partSize;
      if (S) {
        if (p.Shape === 'Sphere') {
          const partial = p.ShapePartial;
          const cz = 1 - 2 * partial * r(), sz = Math.sqrt(Math.max(0, 1 - cz * cz)), a = r() * 2 * Math.PI;
          // cap is centred on the EmissionDirection axis (Top by default)
          let n = [Math.cos(a) * sz, cz, Math.sin(a) * sz];
          if (p.EmissionDirection !== 'Top') n = alignTo(n, dir);
          const k = p.ShapeStyle === 'Surface' ? 1 : Math.cbrt(r());
          pos = [n[0] * S[0] / 2 * k, n[1] * S[1] / 2 * k, n[2] * S[2] / 2 * k];
          dir = io(n, p.ShapeInOut, r);
        } else if (p.Shape === 'Cylinder') {
          const a = r() * 2 * Math.PI, k = p.ShapeStyle === 'Surface' ? 1 : Math.sqrt(r());
          const n = [Math.cos(a), 0, Math.sin(a)];
          pos = [n[0] * S[0] / 2 * k, (r() - 0.5) * S[1], n[2] * S[2] / 2 * k];
          dir = io(n, p.ShapeInOut, r);
        } else if (p.Shape === 'Disc') {
          const a = r() * 2 * Math.PI, k = p.ShapeStyle === 'Surface' ? 1 : Math.sqrt(r());
          pos = [Math.cos(a) * S[0] / 2 * k, 0, Math.sin(a) * S[2] / 2 * k];
          dir = io(dir, p.ShapeInOut, r);
        } else { // Box
          pos = [(r() - 0.5) * S[0], (r() - 0.5) * S[1], (r() - 0.5) * S[2]];
          dir = io(dir, p.ShapeInOut, r);
        }
      }
      if (useSpread && (p.SpreadAngle[0] || p.SpreadAngle[1])) dir = spread(dir, p.SpreadAngle, r);
      if (this.rotated) {
        const v = new THREE.Vector3(...pos).applyQuaternion(this.quat), w = new THREE.Vector3(...dir).applyQuaternion(this.quat);
        pos = [v.x, v.y, v.z]; dir = [w.x, w.y, w.z];
      }
      const sp = range(p.Speed, r);
      const life = range(p.Lifetime, r);
      const nFrames = this.grid * this.grid;
      this.parts.push({
        id: this.uid++,
        x: this.origin.x + pos[0], y: this.origin.y + pos[1], z: this.origin.z + pos[2],
        vx: dir[0] * sp, vy: dir[1] * sp, vz: dir[2] * sp, dx: dir[0], dy: dir[1], dz: dir[2],
        age: 0, life, rot: range(p.Rotation, r) * DEG, rs: range(p.RotSpeed, r) * DEG,
        es: r() * 2 - 1, et: r() * 2 - 1, eq: r() * 2 - 1,
        fps: range(p.FlipbookFramerate, r), f0: p.FlipbookStartRandom ? Math.floor(r() * nFrames) : 0,
      });
    }
    step(dt, t) {
      const p = this.p, L = this.layer;
      if (L.rate) for (const w of L.rate) if (t >= w[0] && t < w[1]) {
        this.acc += w[2] * dt;
        const n = Math.floor(this.acc); this.acc -= n; this.emit(n);
      }
      const ax = p.Acceleration[0], ay = p.Acceleration[1], az = p.Acceleration[2];
      const drag = p.Drag ? Math.pow(2, -p.Drag * dt) : 1;
      const out = [];
      for (const q of this.parts) {
        q.age += dt;
        if (q.age >= q.life) continue;
        q.vx = (q.vx + ax * dt) * drag; q.vy = (q.vy + ay * dt) * drag; q.vz = (q.vz + az * dt) * drag;
        q.x += q.vx * dt; q.y += q.vy * dt; q.z += q.vz * dt;
        const s = Math.hypot(q.vx, q.vy, q.vz);
        if (s > 1e-4) { q.dx = q.vx / s; q.dy = q.vy / s; q.dz = q.vz / s; }
        q.rot += q.rs * dt;
        out.push(q);
      }
      this.parts = out;
    }
    draw(cam, lightLevel) {
      const p = this.p, P = this.pos, U = this.uv, C = this.col, g = this.grid, nF = g * g;
      const cp = cam.position, e = cam.matrixWorld.elements;
      const R = [e[0], e[1], e[2]], Up = [e[4], e[5], e[6]], F = [-e[8], -e[9], -e[10]];
      const parts = this.parts;
      for (const q of parts) q.depth = (q.x - cp.x) * F[0] + (q.y - cp.y) * F[1] + (q.z - cp.z) * F[2];
      parts.sort((a, b) => b.depth - a.depth);
      const li = p.LightInfluence ? 1 + (lightLevel - 1) * p.LightInfluence : 1;
      let n = 0;
      for (const q of parts) {
        const k = q.age / q.life;
        const size = Math.max(0, evalNum(p.Size, k, q.es));
        const tr = evalNum(p.Transparency, k, q.et);
        const sq = p.Squash ? evalNum(p.Squash, k, q.eq) : 0;
        const hgt = size * (sq >= 0 ? 1 + sq : 1 / (1 - sq)) / 2;
        const wid = size * (sq >= 0 ? 1 / (1 + sq) : 1 - sq) / 2;
        const col = evalCol(p.Color, k);
        let tx = cp.x - q.x, ty = cp.y - q.y, tz = cp.z - q.z;
        const tl = Math.hypot(tx, ty, tz) || 1; tx /= tl; ty /= tl; tz /= tl;
        let ax, ay; // quad half-axes (right, up)
        const o = p.Orientation;
        if (o === 'VelocityParallel') {
          const u = [q.dx, q.dy, q.dz];
          let rr = cross(u, [tx, ty, tz]); rr = norm(rr, R);
          ax = rr; ay = u;
        } else if (o === 'VelocityPerpendicular') {
          const nn = [q.dx, q.dy, q.dz];
          let tt = cross(nn, Math.abs(nn[1]) < 0.99 ? [0, 1, 0] : [1, 0, 0]); tt = norm(tt, R);
          const bb = cross(nn, tt);
          ax = rot2(tt, bb, q.rot, 0); ay = rot2(tt, bb, q.rot, 1);
        } else if (o === 'FacingCameraWorldUp') {
          const up = [0, 1, 0];
          let rr = norm(cross(up, [tx, ty, tz]), R);
          ax = rot2(rr, up, q.rot, 0); ay = rot2(rr, up, q.rot, 1);
        } else {
          ax = rot2(R, Up, q.rot, 0); ay = rot2(R, Up, q.rot, 1);
        }
        const zo = p.ZOffset || 0;
        const cx = q.x + tx * zo, cy = q.y + ty * zo, cz = q.z + tz * zo;
        const b = n * 12;
        for (let c = 0; c < 4; c++) {
          const sx = c === 0 || c === 3 ? -1 : 1, sy = c < 2 ? -1 : 1;
          P[b + c * 3] = cx + ax[0] * wid * sx + ay[0] * hgt * sy;
          P[b + c * 3 + 1] = cy + ax[1] * wid * sx + ay[1] * hgt * sy;
          P[b + c * 3 + 2] = cz + ax[2] * wid * sx + ay[2] * hgt * sy;
        }
        // flipbook frame
        let fr = 0;
        if (nF > 1) {
          const step = Math.floor(q.age * q.fps);
          if (p.FlipbookMode === 'OneShot') fr = Math.min(nF - 1, Math.floor(k * nF));
          else if (p.FlipbookMode === 'PingPong') { const m = (q.f0 + step) % (2 * nF - 2); fr = m < nF ? m : 2 * nF - 2 - m; }
          else if (p.FlipbookMode === 'Random') fr = hash(q.id * 131 + step * 7 + this.seed) % nF;
          else fr = (q.f0 + step) % nF;
        }
        const col0 = fr % g, row = Math.floor(fr / g);
        const u0 = col0 / g, u1 = (col0 + 1) / g, v0 = 1 - (row + 1) / g, v1 = 1 - row / g;
        U.set([u0, v0, u1, v0, u1, v1, u0, v1], n * 8);
        const al = Math.max(0, Math.min(1, 1 - tr));
        for (let c = 0; c < 4; c++) C.set([col[0] * li, col[1] * li, col[2] * li, al], n * 16 + c * 4);
        n++;
      }
      const geo = this.mesh.geometry;
      geo.setDrawRange(0, n * 6);
      geo.attributes.position.needsUpdate = geo.attributes.uv.needsUpdate = geo.attributes.color4.needsUpdate = true;
      this.mesh.visible = n > 0 && !this.hidden;
    }
  }

  function hash(x) { x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); return (x ^ (x >>> 16)) >>> 0; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function norm(v, fb) { const l = Math.hypot(v[0], v[1], v[2]); return l < 1e-6 ? fb : [v[0] / l, v[1] / l, v[2] / l]; }
  function rot2(a, b, t, which) {
    const c = Math.cos(t), s = Math.sin(t);
    return which === 0 ? [a[0] * c + b[0] * s, a[1] * c + b[1] * s, a[2] * c + b[2] * s]
      : [-a[0] * s + b[0] * c, -a[1] * s + b[1] * c, -a[2] * s + b[2] * c];
  }
  function io(n, mode, r) {
    const s = mode === 'Inward' ? -1 : mode === 'InAndOut' ? (r() < 0.5 ? -1 : 1) : 1;
    return [n[0] * s, n[1] * s, n[2] * s];
  }
  function alignTo(n, d) { // rotate a +Y-centred vector so +Y maps onto d
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(...d));
    const v = new THREE.Vector3(...n).applyQuaternion(q); return [v.x, v.y, v.z];
  }
  function spread(d, sa, r) {
    const ax = (r() * 2 - 1) * sa[0] * DEG, ay = (r() * 2 - 1) * sa[1] * DEG;
    let t = norm(cross(d, Math.abs(d[1]) < 0.99 ? [0, 1, 0] : [1, 0, 0]), [1, 0, 0]);
    const b = cross(d, t);
    const v = new THREE.Vector3(...d)
      .applyAxisAngle(new THREE.Vector3(...b), ax)
      .applyAxisAngle(new THREE.Vector3(...t), ay);
    return [v.x, v.y, v.z];
  }


  // ---------------- MeshPart emulation (ForceField / Ink / Neon) ----------------
  const MVERT = `
    varying vec2 vUv; varying vec3 vN; varying vec3 vV;
    void main(){ vUv = uv; vec4 wp = modelMatrix * vec4(position,1.0);
      vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - wp.xyz);
      gl_Position = projectionMatrix * viewMatrix * wp; }`;
  // mode 0 = ForceField (additive, fresnel-boosted, texture drifts), 1 = Ink (alpha blend), 2 = Neon (solid additive)
  const MFRAG = `
    uniform sampler2D map; uniform vec3 color; uniform float alpha, bright, fres, mode; uniform vec2 offset, tile;
    varying vec2 vUv; varying vec3 vN; varying vec3 vV;
    void main(){
      vec4 t = texture2D(map, vUv * tile + offset);
      float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
      if (mode < 0.5) {
        vec3 c = t.rgb * color * bright * alpha * (0.55 + fres * f * f + 0.45);
        gl_FragColor = vec4(c, 0.0);
      } else if (mode < 1.5) {
        float a = t.a * alpha;
        gl_FragColor = vec4(color * a, a);
      } else {
        gl_FragColor = vec4(color * bright * alpha * t.a, 0.0);
      }
    }`;
  const MODES = { ForceField: 0, Ink: 1, Neon: 2 };
  function evalKeys(keys, k, dflt) { // [[k, number|[x,y,z]], ...]
    if (keys === undefined) return dflt;
    if (!Array.isArray(keys) || !Array.isArray(keys[0])) return keys;
    if (k <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) if (k <= keys[i][0]) {
      const a = keys[i - 1], b = keys[i], t = (k - a[0]) / (b[0] - a[0] || 1), e = b[2] === 'in' ? t * t : b[2] === 'out' ? 1 - (1 - t) * (1 - t) : t;
      return Array.isArray(a[1]) ? a[1].map((v, j) => v + (b[1][j] - v) * e) : a[1] + (b[1] - a[1]) * e;
    }
    return keys[keys.length - 1][1];
  }
  class MeshFX {
    constructor(layer, sim) {
      this.layer = layer; this.sim = sim;
      const g = G.VFXMeshes.build(layer.mesh, layer.meshArgs);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(g.P.flat(), 3));
      geo.setAttribute('normal', new THREE.Float32BufferAttribute(g.N.flat(), 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(g.UV.flat(), 2));
      geo.setIndex(g.I);
      this.geo = geo;
      const mode = MODES[layer.material || 'ForceField'];
      this.mode = mode;
      this.inst = (layer.spawns || [0]).map(() => {
        const mat = new THREE.ShaderMaterial({
          uniforms: { map: { value: sim.texture(layer.texture, true) }, color: { value: new THREE.Color(1, 1, 1) }, alpha: { value: 1 }, bright: { value: layer.brightness || 1 }, fres: { value: layer.fresnel === undefined ? 1.2 : layer.fresnel }, mode: { value: mode }, offset: { value: new THREE.Vector2() }, tile: { value: new THREE.Vector2(...(layer.tile || [1, 1])) } },
          vertexShader: MVERT, fragmentShader: MFRAG, transparent: true, depthWrite: false, side: THREE.DoubleSide,
          blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
        });
        const m = new THREE.Mesh(geo, mat);
        m.frustumCulled = false; m.visible = false; m.renderOrder = 5 + (layer.order || 0) * 0.01 + (layer.z || 0);
        sim.scene.add(m);
        return m;
      });
      const R = layer.rotation || [0, 0, 0];
      this.base = new THREE.Quaternion().setFromEuler(new THREE.Euler(R[0] * DEG, R[1] * DEG, R[2] * DEG, 'XYZ'));
      this.axis = new THREE.Vector3(...(layer.spinAxis || [0, 1, 0])).normalize();
      this.hidden = false;
    }
    draw(t) {
      const L = this.layer, life = L.life || 0.5;
      (L.spawns || [0]).forEach((s0, i) => {
        const m = this.inst[i], age = t - s0;
        if (age < 0 || age >= life || this.hidden) { m.visible = false; return; }
        const k = age / life, u = m.material.uniforms;
        const sz = evalKeys(L.size, k, 1), sc = Array.isArray(sz) ? sz : [sz, sz, sz];
        m.scale.set(sc[0], sc[1], sc[2]);
        const P0 = L.position || [0, 0, 0], V = L.velocity || [0, 0, 0];
        m.position.set(P0[0] + V[0] * age, P0[1] + V[1] * age, P0[2] + V[2] * age);
        const spin = typeof L.spin === 'number' ? L.spin * age : evalKeys(L.spin, k, 0);
        m.quaternion.copy(this.base).multiply(new THREE.Quaternion().setFromAxisAngle(this.axis, spin * DEG));
        u.alpha.value = Math.max(0, 1 - evalKeys(L.transparency, k, 0));
        const c = typeof L.color === 'string' || L.color === undefined ? hex(L.color || '#ffffff') : evalCol(L.color, k);
        u.color.value.setRGB(c[0], c[1], c[2]);
        const sc2 = L.scroll || [0, 0];
        u.offset.value.set(sc2[0] * age, sc2[1] * age);
        m.visible = true;
      });
    }
    dispose() { for (const m of this.inst) { this.sim.scene.remove(m); m.material.dispose(); } this.geo.dispose(); }
  }

  class Sim {
    constructor(effect, scene) {
      this.fx = effect; this.scene = scene; this.texCache = {}; this.pending = [];
      this.emitters = []; this.meshes = []; this.items = [];
      effect.layers.forEach((L, i) => {
        if (L.mesh) { const m = new MeshFX(Object.assign({ order: i }, L), this); this.meshes.push(m); this.items.push(m); return; }
        const e = new Emitter(Object.assign({ order: i }, L), this, 1000 + i * 7919);
        scene.add(e.mesh); this.emitters.push(e); this.items.push(e);
      });
      this.reset();
    }
    texture(name, repeat) {
      if (!name) return null;
      if (this.texCache[name]) { if (repeat) { const c = this.texCache[name]; c.wrapS = c.wrapT = THREE.RepeatWrapping; c.needsUpdate = true; } return this.texCache[name]; }
      const t = new THREE.Texture();
      if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
      t.premultiplyAlpha = true; t.anisotropy = 4;
      t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
      const src = G.VFX_TEXDATA && G.VFX_TEXDATA[name];
      if (src) {
        const img = new Image();
        this.pending.push(new Promise((res) => { img.onload = () => { t.image = img; t.needsUpdate = true; res(); }; img.onerror = res; }));
        img.src = src;
      } else if (G.VFXPaint) { // live paint fallback (dev only)
        t.image = G.VFXPaint.build(G.VFXPaint.resolve(name).def)[name]; t.needsUpdate = true;
      }
      return (this.texCache[name] = t);
    }
    dispose() { for (const e of this.emitters) { this.scene.remove(e.mesh); e.mesh.geometry.dispose(); e.mat.dispose(); } for (const m of this.meshes) m.dispose(); }
    reset() { this.t = 0; this.prev = -1e-6; for (const e of this.emitters) e.reset(); }
    step(dt) {
      const t1 = this.t + dt;
      for (const e of this.emitters) {
        for (const em of e.layer.emits || []) if ((this.t === 0 ? em[0] >= 0 : em[0] > this.t) && em[0] <= t1) e.emit(em[1]);
      }
      this.prev = this.t; this.t = t1;
      for (const e of this.emitters) e.step(dt, this.t);
    }
    seek(t, dt) {
      this.reset();
      // t = 0 emits happen on the first step
      while (this.t < t - 1e-9) this.step(Math.min(dt, t - this.t));
    }
    draw(cam, lightLevel) { for (const e of this.emitters) e.draw(cam, lightLevel); for (const m of this.meshes) m.draw(this.t); }
    count() { return this.emitters.reduce((s, e) => s + e.parts.length, 0) + this.meshes.reduce((s, m) => s + m.inst.filter((x) => x.visible).length, 0); }

    // ---- non-particle tracks: light, color correction, impact frames, shake ----
    post(t) {
      const fx = this.fx, out = { lights: [], cc: { b: 0, c: 0, s: 0, tint: [1, 1, 1] }, highlight: null, shake: [0, 0, 0], sky: null };
      for (const L of fx.lights || []) out.lights.push({ L, brightness: Math.max(0, track(L.Brightness, t)) });
      if (fx.stage && fx.stage.swing) out.swing = track(fx.stage.swing, t);
      if (fx.grade && fx.grade.length) {
        const g = fx.grade, at = (j) => g[j];
        let a = g[0], b = g[0], k = 0;
        for (let j = 1; j < g.length; j++) if (t <= g[j][0]) { a = g[j - 1]; b = g[j]; k = (t - a[0]) / (b[0] - a[0] || 1); break; } else { a = b = g[j]; }
        const ta = hex(a[4] || '#ffffff'), tb = hex(b[4] || '#ffffff'), L = (x, y) => x + (y - x) * k;
        out.cc = { b: L(a[1], b[1]), c: L(a[2], b[2]), s: L(a[3], b[3]), tint: [L(ta[0], tb[0]), L(ta[1], tb[1]), L(ta[2], tb[2])] };
        void at;
      }
      for (const f of fx.impactFrames || []) {
        if (t >= f.t && t < f.t + f.dur) {
          out.cc = { b: f.Brightness || 0, c: f.Contrast || 0, s: f.Saturation || 0, tint: hex(f.TintColor || '#ffffff') };
          if (f.Highlight) out.highlight = f.Highlight;
          if (f.Void) out.sky = f.Void;
        }
      }
      for (const s of fx.shakes || []) {
        if (t >= s.t && t < s.t + s.dur) {
          const k = (t - s.t) / s.dur, amp = s.amp * Math.pow(1 - k, 2), w = (t - s.t) * s.freq;
          out.shake = [amp * Math.sin(w * 6.1 + 1.3), amp * Math.sin(w * 7.3 + 4.1) * 0.8, amp * Math.sin(w * 5.2 + 2.2) * 0.5];
        }
      }
      return out;
    }
  }

  G.VFXSim = { Sim, evalNum, evalCol, track, DEFAULTS };
})(typeof window !== 'undefined' ? window : globalThis);
