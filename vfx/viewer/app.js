// Viewport app: Roblox-like scene + post (Bloom, ColorCorrection) + transport + layer UI.
(function (G) {
  'use strict';
  const THREE = G.THREE;
  const FX = G.VFX_EFFECTS[G.VFX_ACTIVE || Object.keys(G.VFX_EFFECTS)[0]];
  const DT = 1 / 60, PAUSE = 0.7;
  const $ = (s) => document.querySelector(s);

  // ---------- renderer ----------
  const canvas = $('#vp');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(G.devicePixelRatio || 1, 2));
  renderer.outputEncoding = THREE.LinearEncoding;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(70, 16 / 9, 0.1, 2000); // Roblox default FOV 70
  camera.position.set(19, 7.5, 25);
  const controls = new THREE.OrbitControls(camera, canvas);
  controls.target.set(0, 6, 0);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.495;
  controls.minDistance = 8; controls.maxDistance = 140;
  controls.update();

  // ---------- environment ----------
  function gradTex(top, bot) {
    const c = document.createElement('canvas'); c.width = 4; c.height = 256;
    const g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 256);
    gr.addColorStop(0, top); gr.addColorStop(1, bot); g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
    return new THREE.CanvasTexture(c);
  }
  function gridTex() {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const g = c.getContext('2d');
    g.fillStyle = '#fff'; g.fillRect(0, 0, 128, 128);
    g.fillStyle = 'rgba(0,0,0,0.13)'; g.fillRect(0, 0, 128, 3); g.fillRect(0, 0, 3, 128);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(100, 100); t.anisotropy = 8;
    return t;
  }
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshLambertMaterial({ map: gridTex() }));
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);
  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
  const sun = new THREE.DirectionalLight(0xffffff, 0.6);
  sun.position.set(-30, 60, 20);
  scene.add(hemi, sun);

  const ENVS = {
    dusk: { label: 'Dusk arena', sky: ['#0f0c1c', '#3a2840'], fog: '#2c2034', ground: '#55515e', hemi: [0x8a80c0, 0x2a2430, 0.75], sun: [0xb0a0ff, 0.35], level: 0.55 },
    day: { label: 'Day baseplate', sky: ['#4f9cf0', '#cfe5ff'], fog: '#cfe5ff', ground: '#a3a2a5', hemi: [0xffffff, 0x7a7a80, 0.85], sun: [0xffffff, 0.6], level: 1 },
    void: { label: 'Black void', sky: ['#050507', '#050507'], fog: '#050507', ground: null, hemi: [0x8080a0, 0x101010, 0.5], sun: [0xffffff, 0.3], level: 0.45 },
  };
  let env = ENVS.dusk, envKey = 'dusk';
  const skyCache = {};
  function setEnv(k) {
    envKey = k; env = ENVS[k];
    scene.background = skyCache[k] || (skyCache[k] = gradTex(env.sky[0], env.sky[1]));
    scene.fog = new THREE.Fog(env.fog, 120, 380);
    ground.visible = !!env.ground;
    if (env.ground) ground.material.color.set(env.ground);
    hemi.color.setHex(env.hemi[0]); hemi.groundColor.setHex(env.hemi[1]); hemi.intensity = env.hemi[2];
    sun.color.setHex(env.sun[0]); sun.intensity = env.sun[1];
  }

  // ---------- R15-proportioned dummy for scale (5.2 studs tall) ----------
  const dummy = new THREE.Group();
  const dMat = new THREE.MeshLambertMaterial({ color: 0xc8c6cc });
  const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const box = (w, h, d, x, y, z, col) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), col ? new THREE.MeshLambertMaterial({ color: col }) : dMat);
    m.position.set(x, y, z); m.userData.mat = m.material; dummy.add(m); return m;
  };
  box(1.2, 1.2, 1.2, 0, 4.6, 0);
  box(2, 1.9, 1, 0, 3.05, 0, 0x8a8890);
  box(1, 1.9, 1, -1.5, 3.05, 0); box(1, 1.9, 1, 1.5, 3.05, 0);
  box(0.95, 2.1, 1, -0.5, 1.05, 0, 0x6a6870); box(0.95, 2.1, 1, 0.5, 1.05, 0, 0x6a6870);
  dummy.position.set(-10, 0, 8);
  dummy.lookAt(0, 0, 0);
  scene.add(dummy);
  function highlight(on, color) {
    dummy.children.forEach((m) => { m.material = on ? hlMat : m.userData.mat; });
    if (on) hlMat.color.set(color);
  }

  // ---------- effect ----------
  const sim = new G.VFXSim.Sim(FX, scene);
  const fxLights = (FX.lights || []).map((L) => {
    const pl = new THREE.PointLight(L.Color, 0, L.Range, 1.2);
    pl.position.fromArray(L.position);
    scene.add(pl);
    return pl;
  });

  // ---------- post: Bloom (Roblox BloomEffect-ish) + ColorCorrectionEffect ----------
  const gl = renderer.getContext();
  const hdr = renderer.capabilities.isWebGL2 && (renderer.extensions.has('EXT_color_buffer_float') || renderer.extensions.has('EXT_color_buffer_half_float'));
  const rtOpts = { type: hdr ? THREE.HalfFloatType : THREE.UnsignedByteType, depthBuffer: true };
  let rtScene, rtA, rtB, rtC, rtD;
  const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2));
  const quadScene = new THREE.Scene(); quadScene.add(quad);
  const VQ = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';
  const bright = new THREE.ShaderMaterial({
    uniforms: { t: { value: null }, th: { value: 1.0 } }, vertexShader: VQ,
    fragmentShader: 'uniform sampler2D t; uniform float th; varying vec2 vUv; void main(){ vec3 c = texture2D(t, vUv).rgb; float l = max(c.r, max(c.g, c.b)); gl_FragColor = vec4(c * max(l - th, 0.0) / max(l, 1e-4), 1.0); }',
  });
  const blur = new THREE.ShaderMaterial({
    uniforms: { t: { value: null }, dir: { value: new THREE.Vector2() } }, vertexShader: VQ,
    fragmentShader: `uniform sampler2D t; uniform vec2 dir; varying vec2 vUv;
      void main(){ vec3 s = texture2D(t, vUv).rgb * 0.227;
        s += (texture2D(t, vUv + dir * 1.38).rgb + texture2D(t, vUv - dir * 1.38).rgb) * 0.316;
        s += (texture2D(t, vUv + dir * 3.23).rgb + texture2D(t, vUv - dir * 3.23).rgb) * 0.070;
        gl_FragColor = vec4(s, 1.0); }`,
  });
  const final = new THREE.ShaderMaterial({
    uniforms: {
      t: { value: null }, b1: { value: null }, b2: { value: null }, bi: { value: 0.55 },
      ccB: { value: 0 }, ccC: { value: 0 }, ccS: { value: 0 }, tint: { value: new THREE.Vector3(1, 1, 1) },
    },
    vertexShader: VQ,
    fragmentShader: `uniform sampler2D t, b1, b2; uniform float bi, ccB, ccC, ccS; uniform vec3 tint; varying vec2 vUv;
      void main(){
        vec3 c = texture2D(t, vUv).rgb + (texture2D(b1, vUv).rgb + texture2D(b2, vUv).rgb) * bi;
        c = min(c, vec3(1.0));
        c = c + ccB;
        c = (c - 0.5) * (1.0 + ccC) + 0.5;
        float g = dot(c, vec3(0.299, 0.587, 0.114));
        c = mix(vec3(g), c, 1.0 + ccS);
        gl_FragColor = vec4(clamp(c * tint, 0.0, 1.0), 1.0);
      }`,
  });
  function pass(mat, target) { quad.material = mat; renderer.setRenderTarget(target); renderer.render(quadScene, quadCam); }
  function sizeTargets(w, h) {
    [rtScene, rtA, rtB, rtC, rtD].forEach((r) => r && r.dispose());
    const pr = renderer.getPixelRatio(), W = Math.max(1, Math.floor(w * pr)), H = Math.max(1, Math.floor(h * pr));
    rtScene = new THREE.WebGLRenderTarget(W, H, Object.assign({ samples: renderer.capabilities.isWebGL2 ? 4 : 0 }, rtOpts));
    rtA = new THREE.WebGLRenderTarget(W >> 1, H >> 1, rtOpts); rtB = new THREE.WebGLRenderTarget(W >> 1, H >> 1, rtOpts);
    rtC = new THREE.WebGLRenderTarget(W >> 2, H >> 2, rtOpts); rtD = new THREE.WebGLRenderTarget(W >> 2, H >> 2, rtOpts);
  }

  // ---------- frame ----------
  function render() {
    const post = sim.post(sim.t);
    post.lights.forEach((l, i) => { fxLights[i].intensity = l.brightness * 0.9; });
    if (post.sky) { scene.background = new THREE.Color(post.sky); } else if (!(scene.background && scene.background.isTexture)) setEnv(envKey);
    ground.visible = !!env.ground;
    highlight(!!post.highlight, post.highlight ? post.highlight.FillColor : '#fff');
    final.uniforms.ccB.value = post.cc.b; final.uniforms.ccC.value = post.cc.c; final.uniforms.ccS.value = post.cc.s;
    final.uniforms.tint.value.set(...post.cc.tint);
    const base = camera.position.clone();
    camera.position.add(new THREE.Vector3(...post.shake).applyQuaternion(camera.quaternion));
    camera.updateMatrixWorld();
    sim.draw(camera, env.level);
    renderer.setRenderTarget(rtScene); renderer.render(scene, camera);
    camera.position.copy(base); camera.updateMatrixWorld();
    bright.uniforms.t.value = rtScene.texture; pass(bright, rtA);
    const blurPass = (src, dst, w, h, dx, dy) => { blur.uniforms.t.value = src.texture; blur.uniforms.dir.value.set(dx / w, dy / h); pass(blur, dst); };
    blurPass(rtA, rtB, rtA.width, rtA.height, 1, 0); blurPass(rtB, rtA, rtA.width, rtA.height, 0, 1);
    blurPass(rtA, rtC, rtC.width, rtC.height, 1, 0); blurPass(rtC, rtD, rtC.width, rtC.height, 0, 1);
    blurPass(rtD, rtC, rtC.width, rtC.height, 2, 0); blurPass(rtC, rtD, rtC.width, rtC.height, 0, 2);
    final.uniforms.t.value = rtScene.texture; final.uniforms.b1.value = rtA.texture; final.uniforms.b2.value = rtD.texture;
    pass(final, null);
  }

  function resize() {
    const wrap = canvas.parentElement, w = wrap.clientWidth, h = wrap.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    sizeTargets(w, h);
  }
  new ResizeObserver(resize).observe(canvas.parentElement);
  resize();
  setEnv('dusk');

  // ---------- transport ----------
  const state = { playing: true, speed: 1, loop: true, wait: 0, acc: 0 };
  const scrub = $('#scrub'), tRead = $('#tread'), fRead = $('#fread'), pRead = $('#pread');
  scrub.max = FX.duration; scrub.step = DT;
  function seek(t) { sim.seek(Math.max(0, Math.min(FX.duration, t)), DT); }
  function setPlaying(p) {
    state.playing = p;
    $('#play').setAttribute('aria-label', p ? 'Pause' : 'Play');
    $('#play').dataset.state = p ? 'pause' : 'play';
  }
  $('#play').onclick = () => { if (!state.playing && sim.t >= FX.duration - 1e-6) sim.reset(); setPlaying(!state.playing); };
  $('#replay').onclick = () => { sim.reset(); state.wait = 0; setPlaying(true); };
  $('#prev').onclick = () => { setPlaying(false); seek(sim.t - DT); };
  $('#next').onclick = () => { setPlaying(false); sim.step(DT); };
  $('#loop').onchange = (e) => { state.loop = e.target.checked; };
  scrub.oninput = () => { setPlaying(false); seek(+scrub.value); };
  document.querySelectorAll('[data-speed]').forEach((b) => (b.onclick = () => {
    state.speed = +b.dataset.speed;
    document.querySelectorAll('[data-speed]').forEach((x) => x.setAttribute('aria-pressed', x === b));
  }));
  $('#env').onchange = (e) => setEnv(e.target.value);
  $('#dummy').onchange = (e) => { dummy.visible = e.target.checked; };
  addEventListener('keydown', (e) => {
    if (e.target.closest('input, textarea, select, button')) return;
    if (e.code === 'Space') { e.preventDefault(); $('#play').click(); }
    if (e.key === 'ArrowLeft') $('#prev').click();
    if (e.key === 'ArrowRight') $('#next').click();
    if (e.key === 'r') $('#replay').click();
  });

  // beat ticks under the scrubber
  const ticks = $('#ticks');
  (FX.beats || []).forEach(([t, label]) => {
    const b = document.createElement('button');
    b.className = 'tick'; b.style.left = (t / FX.duration) * 100 + '%';
    b.title = label; b.setAttribute('aria-label', `Jump to ${t.toFixed(2)}s: ${label}`);
    b.onclick = () => { setPlaying(false); seek(t + 0.001); };
    ticks.appendChild(b);
  });
  const beatList = $('#beats');
  (FX.beats || []).forEach(([t, label]) => {
    const li = document.createElement('li');
    li.innerHTML = `<button type="button"><span class="bt">${t.toFixed(2)}s</span><span>${label}</span></button>`;
    li.firstChild.onclick = () => { setPlaying(false); seek(t + 0.001); };
    beatList.appendChild(li);
  });

  // ---------- layers panel ----------
  const list = $('#layers');
  const roles = [...new Set(FX.layers.map((l) => l.role))];
  function describe(L) {
    const p = L.props, bits = [];
    if (L.emits) bits.push(L.emits.map((e) => `Emit(${e[1]}) @${e[0].toFixed(2)}s`).join(', '));
    if (L.rate) bits.push(L.rate.map((r) => `Rate ${r[2]}/s ${r[0].toFixed(2)}–${r[1].toFixed(2)}s`).join(', '));
    if (p.Orientation && p.Orientation !== 'FacingCamera') bits.push(p.Orientation);
    if (p.FlipbookLayout) bits.push(`${p.FlipbookLayout} ${p.FlipbookMode}`);
    return bits.join(' · ');
  }
  roles.forEach((role) => {
    const h = document.createElement('h3'); h.textContent = role; list.appendChild(h);
    FX.layers.forEach((L, i) => {
      if (L.role !== role) return;
      const em = sim.emitters[i];
      const row = document.createElement('div'); row.className = 'layer';
      const id = 'ly-' + L.name;
      const th = document.createElement('canvas'); th.width = th.height = 40; th.className = 'thumb';
      const src = G.VFXTex.get(L.props.Texture), g = G.VFXTex.grid(L.props.Texture);
      th.getContext('2d').drawImage(src, 0, 0, src.width / g[0], src.height / g[1], 0, 0, 40, 40);
      row.innerHTML = `<input type="checkbox" id="${id}" checked><label for="${id}"><span class="ln">${L.name}</span><span class="lm">${describe(L)}</span><span class="lr">${L.ref || ''}</span></label><button type="button" class="solo" aria-pressed="false">Solo</button>`;
      row.prepend(th);
      const cb = row.querySelector('input');
      cb.onchange = () => { em.hidden = !cb.checked; };
      row.querySelector('.solo').onclick = (e) => {
        const on = e.target.getAttribute('aria-pressed') !== 'true';
        list.querySelectorAll('.solo').forEach((s) => s.setAttribute('aria-pressed', 'false'));
        sim.emitters.forEach((x, j) => { x.hidden = on && j !== i; list.querySelector('#ly-' + FX.layers[j].name).checked = !x.hidden; });
        e.target.setAttribute('aria-pressed', on);
      };
      list.appendChild(row);
    });
  });

  // ---------- textures + luau panels ----------
  const texGrid = $('#textures');
  Object.entries(G.VFXTex.defs).forEach(([name, d]) => {
    if (!FX.layers.some((l) => l.props.Texture === name)) return;
    const fig = document.createElement('figure');
    const c = G.VFXTex.get(name); const img = document.createElement('canvas');
    img.width = img.height = 160; img.getContext('2d').drawImage(c, 0, 0, 160, 160);
    fig.appendChild(img);
    const cap = document.createElement('figcaption');
    cap.innerHTML = `<b>${name}.png</b><span>${c.width}px${d.grid[0] > 1 ? ` · ${d.grid[0]}×${d.grid[1]} flipbook` : ''}</span><span>${d.note}</span>`;
    fig.appendChild(cap); texGrid.appendChild(fig);
  });
  const code = G.VFXLuau.toLuau(FX);
  $('#luau').textContent = code;
  $('#copy').onclick = async () => {
    const btn = $('#copy');
    try { await navigator.clipboard.writeText(code); btn.textContent = 'Copied'; }
    catch (e) { const r = document.createRange(); r.selectNodeContents($('#luau')); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = 'Selected, press Ctrl+C'; }
    setTimeout(() => (btn.textContent = 'Copy Luau'), 1800);
  };
  document.querySelectorAll('[role=tab]').forEach((tab) => (tab.onclick = () => {
    document.querySelectorAll('[role=tab]').forEach((t) => t.setAttribute('aria-selected', t === tab));
    document.querySelectorAll('[role=tabpanel]').forEach((p) => { p.hidden = p.id !== tab.getAttribute('aria-controls'); });
  }));
  $('#stat-layers').textContent = FX.layers.length;
  $('#stat-tex').textContent = new Set(FX.layers.map((l) => l.props.Texture)).size;

  // ---------- loop ----------
  let last = performance.now();
  function tick(now) {
    const real = Math.min(0.1, (now - last) / 1000); last = now;
    if (state.playing) {
      if (sim.t >= FX.duration) {
        if (state.loop) { state.wait += real; if (state.wait > PAUSE) { sim.reset(); state.wait = 0; } }
        else setPlaying(false);
      } else {
        state.acc += real * state.speed;
        while (state.acc >= DT) { sim.step(DT); state.acc -= DT; }
      }
    }
    controls.update();
    render();
    scrub.value = sim.t;
    tRead.textContent = sim.t.toFixed(2) + 's';
    fRead.textContent = 'f' + Math.round(sim.t * 60);
    pRead.textContent = sim.count();
    if (!G.VFX_HEADLESS) requestAnimationFrame(tick);
  }
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { setPlaying(false); seek(0.62); }
  requestAnimationFrame(tick);

  // headless hooks (used by tools/headless.mjs for contact sheets + PNG export)
  G.VFX = {
    sim, setEnv, camera, controls,
    frame(t) { setPlaying(false); seek(t); controls.update(); render(); tRead.textContent = t.toFixed(2) + 's'; },
    texturePNG(name) { return G.VFXTex.get(name).toDataURL('image/png'); },
    luau: code,
  };
})(window);
