// Recreations of the three reference clips. Each clip is several VFX stacked on top of each
// other, so every element is its own standalone PART (preview it alone in the lab), and each clip
// is a COMBO that stacks parts by time, position and scale.
//   CosmicStrike  (video 1)  cosmic attack: aura, star flash, orbit ring, rift tear, shard nova,
//                            energy sphere, shard eruption, arc dome, bubble burst
//   FireworkBurst (video 2)  pink impact, beam, wind ring, ground ring, two firework shells, haze
//   KatanaFlurry  (video 3)  blade glint, wind slashes, ink spike burst, dust, ring slash, fire flash
// Textures are painted by craft/textures.py (headless photo-craft) as white layers.
(function (G) {
  const { stack, steps, flicker, part, compose } = G.VFXSpec;
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};

  // stacked white-layer sprite on a fixed plane (or facing the camera)
  function planeStack(name, ref, o) {
    return stack({
      name, role: 'hero', ref, position: o.pos || [0, 0, 0], rotation: o.rot, emits: o.emits,
      props: {
        Texture: o.tex, FlipbookLayout: o.grid || 'Grid4x4', FlipbookMode: 'OneShot', Orientation: o.facing || 'VelocityPerpendicular',
        EmissionDirection: o.dir || 'Top', Speed: [0.01, 0.01], Lifetime: [o.life, o.life], Rotation: [o.spin || 0, o.spin || 0],
        RotSpeed: [o.rs || 0, o.rs || 0], Size: o.size, ZOffset: o.z || 0,
      },
    }, o.colors);
  }
  // plane normals clustered toward a camera at +X/+Z (normal = +Z rotated by [rx, ry]); in-plane angle via spin
  const FACE = (k) => [((k * 37) % 50) - 25, 34 + ((k * 53) % 36) - 18, 0];
  const COSMIC = (a) => ({
    glow: { Color: '#2a48ff', Transparency: steps([0.5, 0.4, 0.55, 0.45, 0.58, 0.68, 0.8, 0.92], 1) },
    rim: { Color: '#1a2296', LightEmission: 0.3, Transparency: 0.15 + (a || 0) },
    mid: { Color: [[0, '#8aa4ff'], [0.5, '#5a76ff'], [1, '#3442d0']], LightEmission: 0.45, Transparency: a || 0 },
    core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.8, Transparency: steps(flicker(0.03, 0.06, 8, 3)) },
  });
  const NAVY = { glow: { Color: '#3050ff', Transparency: 0.55 }, rim: { Color: '#e4eaff', LightEmission: 0.6, Brightness: 1.3 }, mid: { Color: '#0d1868', LightEmission: 0 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.8 } };
  const STAGE1 = { env: 'sky', bloom: [0.6, 0.9], camera: [13, 6.5, 17], target: [0, 3.6, 0], dummy: { pos: [0, 0, 0], face: [0, 0, 10] } };
  const C = [0, 3.6, 0];

  // =============================================================================== video 1 parts
  part({
    name: 'CosmicAura', duration: 1.6, stage: STAGE1, note: 'Charge-up: swirling ground vortex, blue mist, stardust',
    layers: [
      ...planeStack('GroundVortex', 'Vortex swirling flat on the ground', {
        tex: 'swirl_disk', pos: [0, 0.35, 0], rot: [0, 0, 0], emits: [[0, 1]], life: 1.2, size: 18, rs: 120,
        colors: { glow: { Color: '#2a44ff', Transparency: 0.55 }, rim: { Color: '#1a2296', LightEmission: 0.3, Transparency: 0.4 }, mid: { Color: '#6a86ff', LightEmission: 0.6 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } },
      }),
      { name: 'Mist', ref: 'Blue mist pooling at the feet', position: [0, 0.8, 0], part: { Size: [9, 0.2, 9] }, rate: [[0, 1.2, 30]],
        props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [75, 75], Speed: [3, 8], Drag: 1.5, Lifetime: [0.9, 1.3], Rotation: [0, 360], RotSpeed: [-30, 30], Size: [[0, 4], [1, 10, 2]], Color: [[0, '#5a74e8'], [1, '#22308a']], LightEmission: 0.3, Transparency: [[0, 0.45], [0.6, 0.65], [1, 1]], ZOffset: -2 } },
      { name: 'Stardust', ref: 'Twinkling cosmic dust drifting up', position: C, part: { Size: [12, 8, 12] }, rate: [[0, 1.4, 28]],
        props: { Texture: 'sparkle', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [14, 22], Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [40, 40], Speed: [1, 4], Lifetime: [0.4, 0.9], Size: [[0, 0.3, 0.2], [0.3, 0.9, 0.4], [1, 0.2]], Color: '#d8e2ff', LightEmission: 1, Brightness: 2.2, ZOffset: 2 } },
      { name: 'Bokeh', ref: 'Soft glowing orbs', position: C, part: { Size: [14, 9, 14] }, rate: [[0.1, 1.4, 10]],
        props: { Texture: 'bokeh', Shape: 'Box', Speed: [0.5, 2], Lifetime: [0.4, 0.8], Size: [[0, 0.3, 0.2], [0.4, 1.2, 0.5], [1, 0.2]], Color: '#b4c4ff', LightEmission: 1, Brightness: 2, ZOffset: 2 } },
    ],
  });
  part({
    name: 'StarFlash', duration: 0.35, stage: STAGE1, note: 'Navy 4-point star with white edges + glint + blue impact frame',
    impactFrames: [{ t: 0, dur: 0.034, Brightness: 0.3, Contrast: 0.4, Saturation: 0.3, TintColor: '#b8c8ff' }],
    shakes: [{ t: 0.02, dur: 0.3, amp: 0.45, freq: 26 }],
    lights: [{ name: 'Flash', position: C, Color: '#7a90ff', Range: 30, Brightness: [[0, 0], [0.01, 6], [0.3, 0]] }],
    layers: [
      ...planeStack('Star', 'Concave navy star, white ridges', { tex: 'star4', grid: 'Grid2x2', pos: C, facing: 'FacingCamera', emits: [[0, 1]], life: 0.26, size: 14, z: 3,
        colors: { glow: { Color: '#3a5cff', Transparency: 0.35 }, rim: { Color: '#f0f4ff', LightEmission: 0.6, Brightness: 1.5 }, mid: { Color: '#0c1660', LightEmission: 0 }, core: { Color: '#eaff8a', LightEmission: 1, Brightness: 2 } } }),
      { name: 'Glint', ref: 'Lens glint on the star', position: C, emits: [[0, 1]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 6], [0.3, 14], [1, 8]], Color: '#ffffff', LightEmission: 1, Brightness: 2.5, ZOffset: 4 } },
    ],
  });
  part({
    name: 'OrbitRing', duration: 0.45, stage: STAGE1, note: 'Thin tilted orbit ring with a travelling bright segment + horizontal line',
    layers: [
      { name: 'Ring', ref: 'Orbit ring (gold-white)', position: C, rotation: [10, 0, -6], emits: [[0, 1]],
        props: { Texture: 'thin_ring', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Loop', FlipbookFramerate: [16, 16], EmissionDirection: 'Top', Orientation: 'VelocityPerpendicular', Speed: [0.01, 0.01], Lifetime: [0.4, 0.4], Rotation: [0, 0], Size: [[0, 10], [0.3, 17], [1, 19]], Color: '#fff0b0', LightEmission: 1, Brightness: 2, Transparency: [[0, 0], [0.6, 0.2], [1, 1]] } },
      { name: 'HorizonLine', ref: 'Thin line across the ring', position: C, rotation: [0, 0, -90], emits: [[0.02, 1]],
        props: { Texture: 'line', EmissionDirection: 'Top', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.3, 0.3], Size: [[0, 10], [0.2, 26], [1, 22]], Color: '#e8f0ff', LightEmission: 1, Brightness: 2.2, Transparency: [[0, 0], [1, 1]], ZOffset: 1 } },
    ],
  });
  part({
    name: 'RiftTear', duration: 0.5, stage: STAGE1, note: 'Jagged navy tear ripping horizontally across the attack',
    layers: [...planeStack('Rift', 'Jagged rift with lit edges', { tex: 'rift', pos: C, facing: 'FacingCamera', emits: [[0, 1]], life: 0.45, size: 22, z: 1.5, colors: NAVY })],
  });
  part({
    name: 'ShardNova', duration: 0.6, stage: STAGE1, note: 'Navy blade shards radiate out, black ink crescents slash across',
    layers: [
      ...planeStack('Nova', 'Radiating navy shards with lit edges', { tex: 'shard_nova', pos: C, facing: 'FacingCamera', emits: [[0, 1]], life: 0.5, size: 16, z: 0.5, colors: NAVY }),
      { name: 'InkCrescents', ref: 'Black calligraphic crescents', position: C, rotation: [0, 32, 0], part: { Size: [1, 1, 1] }, emits: [[0.02, 3]],
        props: { Texture: 'ink_arc', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', EmissionDirection: 'Back', SpreadAngle: [40, 40], Orientation: 'VelocityPerpendicular', Speed: [0.01, 0.01], Lifetime: [0.42, 0.5], Rotation: [0, 360], Size: [[0, 13, 2.5], [1, 15, 2.5]], Color: '#030408', LightEmission: 0, ZOffset: 1 } },
      ...[0, 1, 2].flatMap((k) => planeStack(`Blade${k + 1}`, 'Serrated navy blade with white teeth + screentone', {
        tex: 'saw_fan', dir: 'Back', pos: C, rot: FACE(k + 21), emits: [[0.04 + k * 0.06, 1]], life: 0.45, size: 13, spin: 40 + k * 110, z: 0.5, colors: NAVY })),
    ],
  });
  part({
    name: 'EnergySphere', duration: 0.9, stage: STAGE1, note: 'Swirling cosmic vortex wrapped in feathery energy swooshes, hairlines and flecks',
    lights: [{ name: 'Glow', position: C, Color: '#5a78ff', Range: 32, Brightness: [[0, 1], [0.05, 5], [0.15, 3.4], [0.25, 4.4], [0.4, 3], [0.9, 0]] }],
    layers: [
      ...planeStack('Vortex', 'Cosmic vortex at the core', { tex: 'energy_swirl', pos: C, facing: 'FacingCamera', emits: [[0, 1]], life: 0.85, size: 12, rs: 160, z: -0.5,
        colors: { glow: { Color: '#2a40ff', Transparency: 0.6 }, rim: { Color: '#1a2296', LightEmission: 0.3, Transparency: 0.3 }, mid: { Color: '#5a74ff', LightEmission: 0.5, Transparency: 0.1 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } } }),
      ...[0, 1, 2, 3, 4, 5].flatMap((k) => planeStack(`Swoosh${k + 1}`, 'Feathery energy swoosh', {
        tex: 'wisp_arc', dir: 'Back', pos: C, rot: FACE(k + 1), emits: [[k * 0.045, 1]], life: 0.6, size: 13 + (k % 3) * 2.5, spin: k * 61, colors: COSMIC() })),
      { name: 'InkLines', ref: 'Black hairlines cutting through', position: C, part: { Size: [1, 1, 1] }, emits: [[0.01, 3], [0.22, 2]],
        props: { Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.22, 0.34], Size: [[0, 14], [0.2, 24, 3], [1, 22, 3]], Color: '#04050a', LightEmission: 0, ZOffset: 1.2 } },
      { name: 'LightLines', ref: 'White hairlines', position: C, part: { Size: [1, 1, 1] }, emits: [[0.03, 3], [0.25, 2]],
        props: { Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.2, 0.3], Size: [[0, 12], [0.2, 20, 3], [1, 18, 3]], Color: '#e8f0ff', LightEmission: 1, Brightness: 2.2, ZOffset: 1.3 } },
      { name: 'Flecks', ref: 'White and yellow-green flecks', position: C, part: { Size: [5, 5, 5] }, emits: [[0, 24]], rate: [[0.05, 0.6, 22]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [16, 40], Drag: 4, Lifetime: [0.25, 0.5], Orientation: 'VelocityParallel', Size: [[0, 1.3, 0.5], [1, 0.3]], Color: [[0, '#ffffff'], [0.3, '#e6ff70'], [1, '#7aa0ff']], LightEmission: 1, Brightness: 2.5, ZOffset: 2 } },
      { name: 'MistBurst', ref: 'Mist blown out', position: C, part: { Size: [4, 4, 4] }, emits: [[0.02, 10]],
        props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Sphere', Speed: [10, 18], Drag: 3, Lifetime: [0.7, 0.9], Rotation: [0, 360], Size: [[0, 5], [1, 11, 2]], Color: [[0, '#5a70d8'], [1, '#22308a']], LightEmission: 0.2, Transparency: [[0, 0.45], [1, 1]], ZOffset: -1.5 } },
    ],
  });
  part({
    name: 'ShardEruption', duration: 0.6, stage: STAGE1, note: 'Fan of navy shards erupting from a bright base',
    shakes: [{ t: 0, dur: 0.25, amp: 0.35, freq: 28 }],
    layers: [
      ...planeStack('Eruption', 'Shards bursting up from the ground', { tex: 'shard_fan', pos: [0, 7.2, 0], facing: 'FacingCameraWorldUp', emits: [[0, 1]], life: 0.5, size: 16, z: 0.5,
        colors: { glow: { Color: '#3a6cff', Transparency: 0.5 }, rim: { Color: '#e8f0ff', LightEmission: 0.6, Brightness: 1.4 }, mid: { Color: '#14247a', LightEmission: 0 }, core: { Color: '#e8fcff', LightEmission: 1, Brightness: 2 } } }),
      { name: 'BaseGlint', ref: 'Gold-white glint at the base', position: [0, 1.2, 0], emits: [[0.02, 1]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 4], [0.3, 9], [1, 5]], Color: '#fff4a0', LightEmission: 1, Brightness: 2.5, ZOffset: 3 } },
    ],
  });
  part({
    name: 'ArcDome', duration: 0.6, stage: STAGE1, note: 'Huge translucent arcs sweeping over the head',
    layers: [0, 1].flatMap((k) => planeStack(`Dome${k + 1}`, 'Giant translucent arc', {
      tex: 'wisp_arc', dir: 'Back', pos: [0, 6.5, 0], rot: [k ? -8 : 10, 30 + k * 12, 0], emits: [[k * 0.06, 1]], life: 0.55, size: 22 + k * 3, spin: 0, colors: COSMIC(0.45) })),
  });
  part({
    name: 'BubbleBurst', duration: 1.0, stage: STAGE1, note: 'Glassy energy bubbles swell and pop, late swooshes',
    layers: [
      ...planeStack('Bubbles', 'Glassy bubbles', { tex: 'blobs', pos: [0, 3.2, 0], facing: 'FacingCamera', emits: [[0, 1]], life: 0.85, size: 13, z: 1,
        colors: { glow: { Color: '#2a44ff', Transparency: 0.85 }, rim: { Color: '#9cb0ff', LightEmission: 0.5, Brightness: 0.9, Transparency: 0.2 }, mid: { Color: '#3a54d0', LightEmission: 0.1, Transparency: 0.65 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.2, Transparency: 0.2 } } }),
      ...[0, 1].flatMap((k) => planeStack(`LateSwoosh${k + 1}`, 'Late swooshes around the bubbles', {
        tex: 'wisp_arc', dir: 'Back', pos: C, rot: FACE(k + 31), emits: [[0.04 + k * 0.08, 1]], life: 0.6, size: 15, spin: 200 + k * 90, colors: COSMIC(0.15) })),
    ],
  });

  G.VFX_EFFECTS.CosmicStrike = compose({ name: 'CosmicStrike', version: 1, stage: STAGE1, duration: 3.0,
    note: 'Video 1: a cosmic combo built from 9 stacked parts' }, [
    { part: 'CosmicAura', t: 0, label: 'Aura charges' },
    { part: 'EnergySphere', t: 0.12, scale: 0.65, tag: 'ChargeSphere', label: 'Small sphere spins up' },
    { part: 'StarFlash', t: 0.32, label: 'Star flash' },
    { part: 'OrbitRing', t: 0.4, label: 'Orbit ring' },
    { part: 'RiftTear', t: 0.48, label: 'Rift tears across' },
    { part: 'ShardNova', t: 0.6, label: 'Shard nova + ink' },
    { part: 'EnergySphere', t: 0.68, label: 'Energy sphere' },
    { part: 'ShardEruption', t: 1.45, label: 'Shard eruption' },
    { part: 'ArcDome', t: 1.6, label: 'Arc dome' },
    { part: 'BubbleBurst', t: 1.78, label: 'Bubble burst' },
    { part: 'CosmicAura', t: 1.9, scale: 0.8, tag: 'Afterglow', label: 'Afterglow' },
  ]);

  // =============================================================================== video 2 parts
  const STAGE2 = { env: 'night', bloom: [1.0, 0.75], camera: [3, 9, 30], target: [0, 8, -2], dummy: { pos: [1.5, 0, 1], face: [-10, 0, 10] } };
  const H = [0, 5.5, 0];
  part({
    name: 'PinkImpact', duration: 0.8, stage: STAGE2, note: 'White-hot pink hit: flare, pink swooshes, cyan/pink shards, glints',
    lights: [{ name: 'Hit', position: H, Color: '#ffb8f0', Range: 40, Brightness: [[0, 0], [0.01, 8], [0.25, 3], [0.8, 0]] }],
    impactFrames: [{ t: 0, dur: 0.034, Brightness: 0.25, Contrast: 0.2, Saturation: 0.1, TintColor: '#ffe8fa' }],
    shakes: [{ t: 0.01, dur: 0.4, amp: 0.6, freq: 26 }],
    layers: [
      { name: 'Flare', ref: 'White-hot lens flare', position: H, emits: [[0, 1]],
        props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.3, 0.3], Rotation: [0, 0], Size: [[0, 6], [0.15, 12], [1, 8]], Color: '#ffe0f6', LightEmission: 1, Brightness: 1.6, Transparency: [[0, 0], [0.5, 0.15], [1, 1]], ZOffset: 3 } },
      ...[0, 1, 2].flatMap((k) => planeStack(`Swoosh${k + 1}`, 'White-pink feathery swooshes', {
        tex: 'wisp_arc', dir: 'Back', pos: H, rot: [FACE(k + 41)[0], FACE(k + 41)[1] - 30, 0], emits: [[k * 0.05, 1]], life: 0.5, size: 10 + k * 1.5, spin: k * 95,
        colors: { glow: { Color: '#ff3ad0', Transparency: 0.55 }, rim: { Color: '#8a1880', LightEmission: 0.2, Transparency: 0.2 }, mid: { Color: [[0, '#ff9ef0'], [1, '#e050d0']], LightEmission: 0.45 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } } })),
      { name: 'CyanShards', ref: 'Cyan shard streaks', position: H, part: { Size: [2, 2, 2] }, emits: [[0.01, 36]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [40, 90], Drag: 5, Lifetime: [0.25, 0.5], Orientation: 'VelocityParallel', Size: [[0, 3, 1], [1, 0.4]], Color: [[0, '#ffffff'], [1, '#40e8ff']], LightEmission: 1, Brightness: 3 } },
      { name: 'PinkShards', ref: 'Pink and gold sparks', position: H, part: { Size: [2, 2, 2] }, emits: [[0.01, 50]], rate: [[0.04, 0.55, 40]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [25, 70], Drag: 4, Acceleration: [0, -10, 0], Lifetime: [0.3, 0.7], Orientation: 'VelocityParallel', Size: [[0, 2, 0.8], [1, 0.3]], Color: [[0, '#ffffff'], [0.4, '#ff8ae6'], [1, '#ffb040']], LightEmission: 1, Brightness: 3 } },
      { name: 'Glints', ref: 'Glints popping around the hit', position: H, part: { Size: [9, 7, 9] }, rate: [[0.02, 0.6, 26]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [0, 0], Lifetime: [0.14, 0.22], Rotation: [0, 0], Size: [[0, 2.5, 1.2], [1, 2.5, 1.2]], Color: '#fff4ff', LightEmission: 1, Brightness: 2.6, ZOffset: 3 } },
    ],
  });
  part({
    name: 'PinkBeam', duration: 0.45, stage: STAGE2, note: 'Long diagonal pink beam',
    layers: [{ name: 'Beam', ref: 'Pink beam', position: H, rotation: [0, 0, -38], emits: [[0, 1]],
      props: { Texture: 'line', EmissionDirection: 'Top', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.4, 0.4], Size: [[0, 18], [0.12, 50], [1, 44]], Color: '#ff6ae4', LightEmission: 1, Brightness: 3, Transparency: [[0, 0], [0.5, 0.1], [1, 1]], ZOffset: 2 } }],
  });
  part({
    name: 'WindRing', duration: 0.7, stage: STAGE2, note: 'Pale wind swooshes ringing the impact',
    layers: [0, 1].flatMap((k) => planeStack(`Wind${k + 1}`, 'Pale wind swoosh', {
      tex: 'trail_arc', pos: [0, 2.4, 0], rot: [k ? 8 : -6, k * 140, k ? -10 : 12], emits: [[k * 0.06, 1]], life: 0.6, size: 16 + k * 3, spin: k * 150,
      colors: { glow: { Color: '#c8c8e0', Transparency: 0.75 }, rim: { Color: '#4a4a5c', LightEmission: 0, Transparency: 0.55 }, mid: { Color: '#d8d8e8', LightEmission: 0.3, Transparency: 0.35 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } } })),
  });
  part({
    name: 'GroundRing', duration: 1.9, stage: STAGE2, note: 'Shockwave swirl on the ground + ember streaks skidding out',
    layers: [
      ...planeStack('Swirl', 'Ground shockwave swirl', { tex: 'swirl_disk', pos: [0, 0.3, 0], rot: [0, 0, 0], emits: [[0, 1]], life: 0.9, size: 18, rs: -90,
        colors: { glow: { Color: '#ffb0e0', Transparency: 0.7 }, rim: { Color: '#202028', LightEmission: 0, Transparency: 0.3 }, mid: { Color: '#d8d0e0', LightEmission: 0.3, Transparency: 0.25 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } } }),
      { name: 'Embers', ref: 'Orange ember streaks skidding across the ground', position: [0, 0.5, 0], part: { Size: [6, 0.4, 6] }, emits: [[0.02, 30]],
        props: { Texture: 'spark', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [80, 80], Speed: [10, 26], Drag: 2.5, Acceleration: [0, -14, 0], Lifetime: [0.8, 1.8], Orientation: 'VelocityParallel', Size: [[0, 1.4, 0.4], [1, 0.4]], Color: [[0, '#ffd080'], [1, '#ff4a10']], LightEmission: 1, Brightness: 2.5 } },
    ],
  });
  part({
    name: 'Haze', duration: 2.6, stage: STAGE2, note: 'Grey smoke haze left behind',
    layers: [{ name: 'Haze', ref: 'Grey haze', position: [0, 2.5, 0], part: { Size: [8, 3, 8] }, emits: [[0, 12]], rate: [[0.1, 0.9, 8]],
      props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [2, 6], Lifetime: [1.2, 1.7], Rotation: [0, 360], Size: [[0, 6], [1, 13, 2]], Color: '#a8a4b4', LightEmission: 0.15, Transparency: [[0, 0.55], [1, 1]], ZOffset: -3 } }],
  });
  const firework = (name, cols, n) => part({
    name, previewAt: [0, 10, -4], duration: 2.0, stage: STAGE2, note: 'Firework shell: flare, streaks on a sphere, then twinkling stars drifting down',
    lights: [{ name: 'Shell', position: [0, 0, 0], Color: cols[1], Range: 50, Brightness: [[0, 0], [0.1, 5], [0.9, 1], [1.9, 0]] }],
    layers: [
      { name: 'Flare', ref: 'Sun-like flare before the burst', position: [0, 0, 0], emits: [[0, 1]],
        props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.42, 0.42], Rotation: [0, 0], Size: [[0, 5], [0.3, 13], [1, 7]], Color: cols[0], LightEmission: 1, Brightness: 1.5, Transparency: [[0, 0], [0.6, 0.2], [1, 1]] } },
      { name: 'Streaks', ref: 'Streaks shoot out on a sphere', position: [0, 0, 0], part: { Size: [1, 1, 1] }, emits: [[0.1, n]],
        props: { Texture: 'spark', Shape: 'Sphere', ShapeStyle: 'Surface', Speed: [30, 38], Drag: 2.6, Lifetime: [0.35, 0.5], Orientation: 'VelocityParallel', Size: [[0, 2.2, 0.4], [1, 0.8]], Color: [[0, '#ffffff'], [1, cols[1]]], LightEmission: 1, Brightness: 3 } },
      { name: 'Stars', ref: 'Twinkling stars drift down and fade', position: [0, 0, 0], part: { Size: [1, 1, 1] }, emits: [[0.1, n]],
        props: { Texture: 'sparkle', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [14, 20], Shape: 'Sphere', ShapeStyle: 'Surface', Speed: [30, 38], Drag: 2.6, Acceleration: [0, -5, 0], Lifetime: [1.0, 1.7], Size: [[0, 0.9, 0.3], [1, 0.5, 0.2]], Color: [[0, '#ffffff'], [0.25, cols[1]], [1, cols[2]]], LightEmission: 1, Brightness: 2.6, Transparency: [[0, 0], [0.7, 0.2], [1, 1]] } },
    ],
  });
  firework('FireworkPink', ['#ffa8f0', '#ff70e0', '#7a68ff'], 200);
  firework('FireworkGold', ['#ffcc70', '#ffc040', '#ff7a20'], 200);
  G.VFX_EFFECTS.FireworkBurst = compose({ name: 'FireworkBurst', version: 2, stage: STAGE2, note: 'Video 2: impact combo stacked from 7 parts' }, [
    { part: 'PinkImpact', t: 0.06, label: 'Pink impact' },
    { part: 'PinkBeam', t: 0.08, label: 'Beam' },
    { part: 'WindRing', t: 0.1, label: 'Wind ring' },
    { part: 'GroundRing', t: 0.08, label: 'Ground ring + embers' },
    { part: 'Haze', t: 0.12, label: 'Haze' },
    { part: 'FireworkPink', t: 0.24, at: [-11, 14, -6], label: 'Pink shell' },
    { part: 'FireworkGold', t: 0.32, at: [12, 15, -8], label: 'Gold shell' },
  ]);

  // =============================================================================== video 3 parts
  const STAGE3 = { env: 'sky', bloom: [0.9, 0.8], camera: [9, 5.5, -13], target: [0.8, 3.4, -1.5], dummy: { pos: [0, 0, 0], face: [0, 0, -10], sword: 'katana' },
    swing: [[0, 110], [0.05, 110], [0.1, -40], [0.28, -40], [0.32, 140], [0.5, 140], [0.55, 20], [0.85, 110], [0.9, -40], [1.4, -40]] };
  const WIND = { glow: { Color: '#a8b8c8', Transparency: 0.85 }, rim: { Color: '#2c323e', LightEmission: 0, Transparency: 0.55 }, mid: { Color: '#a6b0bc', LightEmission: 0, Transparency: 0.45 }, core: { Color: '#ffffff', LightEmission: 0.8, Brightness: 1.2, Transparency: 0.3 } };
  part({
    name: 'BladeGlint', previewAt: [1.5, 5, -1], duration: 0.25, stage: STAGE3, note: 'Lens glint on the blade tip',
    layers: [{ name: 'Glint', ref: 'Blade-tip glint', position: [0, 0, 0], emits: [[0, 1]],
      props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 3], [0.3, 8], [1, 5]], Color: '#ffffff', LightEmission: 1, Brightness: 3, ZOffset: 3 } }],
  });
  const windSlash = (name, rot, spin, at) => part({
    name, previewAt: at, duration: 0.5, stage: STAGE3, note: 'Translucent grey wind trail of a katana cut',
    shakes: [{ t: 0.02, dur: 0.15, amp: 0.25, freq: 28 }],
    layers: planeStack('Trail', 'Wind slash trail', { tex: 'trail_arc', rot, emits: [[0, 1]], life: 0.45, size: 14, spin, colors: WIND }),
  });
  windSlash('WindSlashA', [-55, 0, -30], 180, [0.8, 3.2, -2.2]);
  windSlash('WindSlashB', [-60, 0, 28], 20, [0.4, 3.0, -2.0]);
  part({
    name: 'InkSpikeBurst', previewAt: [0, 3.4, 0.6], duration: 0.3, stage: STAGE3, note: 'Black jagged spike burst behind the character',
    layers: [{ name: 'Spikes', ref: 'Ink spike burst', position: [0, 0, 0], emits: [[0, 1]],
      props: { Texture: 'ink_spikes', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.24, 0.24], Rotation: [0, 0], Size: [[0, 9], [1, 13]], Color: '#06060a', LightEmission: 0, Transparency: [[0, 0.05], [1, 0.4]], ZOffset: -2 } }],
  });
  part({
    name: 'DustKick', previewAt: [0, 0.8, 0], duration: 1.3, stage: STAGE3, note: 'Dust kicked up at the feet',
    layers: [{ name: 'Dust', ref: 'Dust', position: [0, 0, 0], part: { Size: [3, 0.3, 3] }, emits: [[0, 8]],
      props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [70, 70], Speed: [5, 11], Drag: 2.5, Lifetime: [0.8, 1.2], Rotation: [0, 360], Size: [[0, 3], [1, 8, 1.5]], Color: '#8c7c6a', LightEmission: 0, LightInfluence: 0.6, Transparency: [[0, 0.2], [1, 1]], ZOffset: -1 } }],
  });
  part({
    name: 'RingSlash', previewAt: [0.4, 3.4, -1.6], duration: 0.7, stage: STAGE3, note: 'Dark vortex ring slash with white highlight strands + glint',
    layers: [
      ...planeStack('Ring', 'Dark vortex ring', { tex: 'ring_slash', rot: [-80, 0, 0], emits: [[0, 1]], life: 0.65, size: 12, rs: -220,
        colors: { glow: { Color: '#8c9cb0', Transparency: 0.9 }, rim: { Color: '#06070a', LightEmission: 0, Transparency: 0.15 }, mid: { Color: '#3a404c', LightEmission: 0, Transparency: 0.3 }, core: { Color: '#ffffff', LightEmission: 0.9, Brightness: 1.3, Transparency: 0.2 } } }),
      { name: 'EdgeGlint', ref: 'Glint on the ring edge', position: [-4, -1, -0.8], emits: [[0.02, 1]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.18, 0.18], Rotation: [0, 0], Size: [[0, 3], [0.3, 7], [1, 4]], Color: '#ffffff', LightEmission: 1, Brightness: 3, ZOffset: 3 } },
    ],
  });
  part({
    name: 'FireFlash', previewAt: [3.6, 5.2, -1.6], duration: 1.0, stage: STAGE3, note: 'Orange fire flash: radial burst, flare, beam, embers, smoke',
    lights: [{ name: 'Fire', position: [0, 0, 0], Color: '#ff8a30', Range: 30, Brightness: [[0, 0], [0.01, 5], [0.15, 4], [0.55, 1], [1.0, 0]] }],
    impactFrames: [{ t: 0, dur: 0.034, Brightness: 0.3, Contrast: 0.3, Saturation: 0.2, TintColor: '#fff0e0' }],
    shakes: [{ t: 0.01, dur: 0.4, amp: 0.8, freq: 24 }],
    layers: [
      ...planeStack('Burst', 'Radial fire burst', { tex: 'fire_burst', facing: 'FacingCamera', emits: [[0, 1]], life: 0.55, size: 13, z: 1,
        colors: { glow: { Color: '#ff5a10', Transparency: 0.35, Brightness: 1.2 }, rim: { Color: '#c82a08', LightEmission: 0.5 }, mid: { Color: '#ff8a20', LightEmission: 0.7, Brightness: 1.1 }, core: { Color: '#fff2d0', LightEmission: 1, Brightness: 2 } } }),
      { name: 'Flare', ref: 'Orange lens flare', position: [0, 0.4, 0], emits: [[0, 1]],
        props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.3, 0.3], Rotation: [0, 0], Size: [[0, 8], [0.2, 16], [1, 10]], Color: '#ffa850', LightEmission: 1, Brightness: 1.6, Transparency: [[0, 0], [1, 1]], ZOffset: 3 } },
      { name: 'Beam', ref: 'Thin red-orange beam shooting up', position: [0.4, -0.2, -0.4], emits: [[0.05, 1]],
        props: { Texture: 'line', EmissionDirection: 'Top', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.36, 0.36], Size: [[0, 8], [0.2, 30], [1, 26]], Color: '#ff4a10', LightEmission: 1, Brightness: 1.4, Transparency: [[0, 0], [0.6, 0.2], [1, 1]], ZOffset: 2 } },
      { name: 'Embers', ref: 'Embers and orange sparks', position: [0, 0, 0], part: { Size: [3, 3, 3] }, emits: [[0, 40]], rate: [[0.05, 0.5, 18]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [14, 46], Drag: 3, Acceleration: [0, -12, 0], Lifetime: [0.3, 0.5], Orientation: 'VelocityParallel', Size: [[0, 1.4, 0.5], [1, 0.3]], Color: [[0, '#fff2c0'], [0.4, '#ffa030'], [1, '#ff3a10']], LightEmission: 1, Brightness: 3 } },
      { name: 'Smoke', ref: 'Brown smoke rolling off', position: [0, -0.7, 0], part: { Size: [4, 2, 4] }, emits: [[0.07, 8]],
        props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [60, 60], Speed: [3, 8], Lifetime: [0.7, 0.9], Rotation: [0, 360], Size: [[0, 5], [1, 11, 2]], Color: '#6a4a38', LightEmission: 0, Transparency: [[0, 0.3], [1, 1]], ZOffset: -1 } },
    ],
  });
  G.VFX_EFFECTS.KatanaFlurry = compose({ name: 'KatanaFlurry', version: 2, stage: STAGE3, note: 'Video 3: katana combo stacked from 7 parts' }, [
    { part: 'BladeGlint', t: 0, at: [2.4, 7.2, -1.2], label: 'Blade glint' },
    { part: 'WindSlashA', t: 0.06, at: [0.8, 3.2, -2.2], label: 'Cut 1' },
    { part: 'InkSpikeBurst', t: 0.08, at: [0, 3.4, 0.6], label: 'Ink spikes' },
    { part: 'DustKick', t: 0.06, at: [0, 0.8, 0], label: 'Dust' },
    { part: 'RingSlash', t: 0.28, at: [0.4, 3.4, -1.6], label: 'Ring slash' },
    { part: 'FireFlash', t: 0.55, at: [3.6, 5.2, -1.6], label: 'Fire flash' },
    { part: 'BladeGlint', t: 0.86, at: [2.4, 7.2, -1.2], tag: 'BladeGlint2', label: 'Glint' },
    { part: 'WindSlashB', t: 0.9, at: [0.4, 3.0, -2.0], label: 'Cut 2' },
    { part: 'InkSpikeBurst', t: 0.9, at: [0, 3.4, 0.6], tag: 'InkSpikeBurst2', label: 'Ink spikes' },
    { part: 'DustKick', t: 0.88, at: [0, 0.8, 0], tag: 'DustKick2', label: 'Dust' },
  ]);
})(typeof window !== 'undefined' ? window : globalThis);
