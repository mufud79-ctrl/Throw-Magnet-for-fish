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
        colors: { glow: { Color: '#2a44ff', Transparency: 0.8 }, rim: { Color: '#1a2296', LightEmission: 0.3, Transparency: 0.7 }, mid: { Color: '#6a86ff', LightEmission: 0.5, Transparency: 0.5 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.2, Transparency: 0.4 } },
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
    layers: [...planeStack('Rift', 'Jagged rift with lit edges', { tex: 'rift', pos: C, facing: 'FacingCamera', emits: [[0, 1]], life: 0.16, size: 22, z: 1.5, colors: NAVY })],
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

  // ---- video 1 on MESHES: ForceField spheres/bands wrap in 3D, the world is graded blue ----
  const { faceRot } = G.VFXSpec;
  const mesh = (name, ref, o) => Object.assign({ name, ref }, o, { props: { Texture: o.texture } });
  const STAGE1B = Object.assign({}, STAGE1, { env: 'cosmic', bloom: [0.45, 1.0], camera: [9, 9.5, 12], target: [0, 3.4, 0], dummy: { pos: [0, 0, 0], face: [0, 0, 10], color: '#151a36' } });
  const BLUEGRADE = [[0, 0, 0, 0, '#ffffff'], [0.08, -0.04, 0.22, 0.12, '#d6deff'], [2.1, -0.04, 0.22, 0.12, '#d6deff'], [2.5, 0, 0, 0, '#ffffff']];
  const BANDS = [[20, 0, 10], [70, 30, -20], [-50, 60, 30], [100, -20, 40], [35, 120, -60], [-80, 10, 70]];
  const slashBand = (name, o) => mesh(name, 'ForceField slash band whipping around', Object.assign({
    mesh: 'band', meshArgs: { arc: 220, inner: 0.62, cone: 0.12 }, texture: 'm_slash', material: 'ForceField', color: '#b8c8ff', brightness: 2.2, fresnel: 0.3,
    life: 0.32, size: [[0, 11], [0.3, 15, 'out'], [1, 16]], transparency: [[0, 0], [0.6, 0.1], [1, 1]],
  }, o));
  const inkBand = (name, o) => mesh(name, 'Black calligraphic band (Ink mesh)', Object.assign({
    mesh: 'band', meshArgs: { arc: 150, inner: 0.8, cone: 0.05 }, texture: 'm_ink', material: 'Ink', color: '#020308',
    life: 0.28, size: [[0, 14], [1, 17]], transparency: [[0, 0], [0.7, 0], [1, 1]],
  }, o));
  part({
    name: 'FlatSlash', duration: 0.5, stage: STAGE1B, grade: BLUEGRADE, note: 'Horizontal energy disc at waist height with black ink riding on it',
    layers: [
      slashBand('Disc', { position: [0, 2.6, 0], rotation: [0, 0, 0], spin: 900, spawns: [0, 0.05], life: 0.36, meshArgs: { arc: 260, inner: 0.55, cone: 0.06 }, size: [[0, 10], [0.3, 15, 'out'], [1, 16]] }),
      inkBand('InkDisc', { position: [0, 2.7, 0], rotation: [0, 0, 0], spin: 800, spawns: [0.03], life: 0.3, size: [[0, 12], [1, 15]] }),
    ],
  });
  part({
    name: 'InkHooks', duration: 0.4, stage: STAGE1B, note: 'Tall black calligraphic hooks rising out of the orb',
    layers: [{ name: 'Hooks', ref: 'Black hooks', position: [0, 6.5, 0], emits: [[0, 2]],
      props: { Texture: 'ink_arc', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.32, 0.36], Rotation: [-120, -60], Size: [[0, 7, 1], [1, 8, 1]], Color: '#030408', LightEmission: 0, ZOffset: 2 } }],
  });
  part({
    name: 'SmallOrb', duration: 0.45, stage: STAGE1B, grade: BLUEGRADE, note: 'Spinning ForceField orb forming around the character',
    layers: [
      mesh('Orb', 'ForceField swirl sphere', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#7a8cff', brightness: 1.4, position: [0, 3.6, 0], rotation: [25, 0, 15], spin: 420, spawns: [0], life: 0.42, size: [[0, 2], [0.4, 7, 'out'], [1, 8]], transparency: [[0, 0.1], [0.7, 0.2], [1, 1]], scroll: [0.5, 0] }),
      slashBand('Wrap', { position: [0, 3.6, 0], rotation: [60, 20, 0], spin: 1100, spawns: [0.05, 0.2], life: 0.2, size: [[0, 6], [1, 9]] }),
    ],
  });
  part({
    name: 'PillarFlash', duration: 0.12, stage: STAGE1B, note: 'Two-frame navy cylinder mesh with a glowing base ring (impact cut)',
    layers: [
      mesh('Column', 'Opaque navy cylinder', { mesh: 'cylinder', texture: 'm_solid', material: 'Ink', color: '#0b1a8c', position: [4.6, 9, 6.2], spawns: [0], life: 0.05, size: [7, 20, 7] }),
      mesh('BaseRing', 'Glowing gold-white base ring', { mesh: 'torus', meshArgs: { tube: 0.06 }, texture: 'm_solid', material: 'ForceField', color: '#fff0a0', brightness: 2.5, position: [4.6, -0.6, 6.2], spawns: [0], life: 0.05, size: [7.4, 4, 7.4] }),
    ],
  });
  part({
    name: 'SpikeCrown', duration: 0.35, stage: STAGE1B, note: 'Huge dark navy spike crown erupting from the character',
    shakes: [{ t: 0, dur: 0.25, amp: 0.6, freq: 28 }],
    layers: planeStack('Crown', 'Spike crown', { tex: 'shard_fan', pos: [0, 11.3, 0], facing: 'FacingCameraWorldUp', emits: [[0, 1]], life: 0.14, size: 25, z: 1,
      colors: { glow: { Color: '#3050ff', Transparency: 0.7 }, rim: { Color: '#c8d8ff', LightEmission: 0.4 }, mid: { Color: '#101c78', LightEmission: 0 }, core: { Color: '#e8fcff', LightEmission: 1, Brightness: 1.8 } } }),
  });
  part({
    name: 'CosmicSphere', duration: 1.0, stage: STAGE1B, grade: BLUEGRADE, note: 'The hero: spinning ForceField spheres wrapped by slash bands and ink bands in 3D, blades, hairlines, bokeh',
    lights: [{ name: 'Sphere', position: [0, 4, 0], Color: '#5a78ff', Range: 34, Brightness: [[0, 2], [0.04, 6], [0.2, 4], [0.35, 5], [0.6, 3.5], [1.0, 0]] }],
    layers: [
      mesh('Orb', 'Outer ForceField swirl sphere', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#4a5cf0', brightness: 0.8, position: [0, 4, 0], rotation: [25, 0, 15], spin: 260, spawns: [0], life: 0.95, size: [[0, 6], [0.12, 11.5, 'out'], [0.8, 12.5], [1, 13]], transparency: [[0, 0.1], [0.75, 0.2], [1, 1]], scroll: [0.35, 0] }),
      mesh('Body', 'Dark navy body behind the glass (Ink mesh)', { mesh: 'sphere', texture: 'm_swirl', material: 'Ink', color: '#0c1450', position: [0, 4, 0], rotation: [10, 0, 30], spin: -200, spawns: [0], life: 0.9, size: [[0, 5], [0.15, 10.5, 'out'], [1, 11]], transparency: [[0, 0.5], [0.8, 0.55], [1, 1]] }),
      mesh('InnerOrb', 'Inner counter-spinning sphere', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#9cb0ff', brightness: 0.6, position: [0, 4, 0], rotation: [-30, 0, 40], spin: -340, spawns: [0], life: 0.9, size: [[0, 4], [0.15, 8.5, 'out'], [1, 9]], transparency: [[0, 0.35], [0.8, 0.45], [1, 1]], scroll: [-0.5, 0.1] }),
      ...BANDS.map((r, k) => slashBand(`Slash${k + 1}`, { position: [0, 4, 0], rotation: r, spin: (k % 2 ? -1 : 1) * (720 + k * 70), color: k % 2 ? '#c8d4ff' : '#8ea6ff', spawns: [0.02 + k * 0.06, 0.45 + k * 0.06] })),
      ...[0, 1, 2].map((k) => inkBand(`Ink${k + 1}`, { position: [0, 4, 0], rotation: BANDS[k * 2].map((v) => v + 25), spin: -650, spawns: [0.08 + k * 0.12, 0.55 + k * 0.1] })),
      ...[0, 1].flatMap((k) => planeStack(`Blade${k + 1}`, 'Navy serrated blade slicing through', {
        tex: 'saw_fan', dir: 'Back', pos: [0, 4, 0], rot: FACE(k + 21), emits: [[0.15 + k * 0.25, 1]], life: 0.4, size: 14, spin: 40 + k * 140, z: 0.6, colors: NAVY })),
      { name: 'InkLines', ref: 'Long black hairlines crossing the sphere', position: [0, 4, 0], part: { Size: [0.2, 0.2, 0.2] }, emits: [[0.1, 2], [0.45, 2]],
        props: { Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.25, 0.35], Size: [[0, 20], [0.15, 30, 3], [1, 28, 3]], Color: '#04050a', LightEmission: 0, ZOffset: 1.5 } },
      { name: 'LightLines', ref: 'White hairlines', position: [0, 4, 0], part: { Size: [0.2, 0.2, 0.2] }, emits: [[0.12, 2], [0.5, 2]],
        props: { Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.2, 0.3], Size: [[0, 18], [0.15, 28, 3], [1, 26, 3]], Color: '#e8f0ff', LightEmission: 1, Brightness: 2, ZOffset: 1.6 } },
      { name: 'Bokeh', ref: 'Bokeh orbs around the sphere', position: [0, 4, 0], part: { Size: [13, 10, 13] }, rate: [[0, 0.9, 14]],
        props: { Texture: 'bokeh', Shape: 'Box', Speed: [0.5, 2], Lifetime: [0.4, 0.8], Size: [[0, 0.3, 0.2], [0.4, 1.3, 0.5], [1, 0.2]], Color: '#b4c4ff', LightEmission: 1, Brightness: 2, ZOffset: 2 } },
      { name: 'Flecks', ref: 'White and yellow-green flecks', position: [0, 4, 0], part: { Size: [6, 6, 6] }, emits: [[0, 18]], rate: [[0.05, 0.7, 16]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [14, 34], Drag: 4, Lifetime: [0.25, 0.5], Orientation: 'VelocityParallel', Size: [[0, 1.3, 0.5], [1, 0.3]], Color: [[0, '#ffffff'], [0.3, '#e6ff70'], [1, '#7aa0ff']], LightEmission: 1, Brightness: 2.4, ZOffset: 2 } },
    ],
  });
  part({
    name: 'Dissolve', duration: 1.0, stage: STAGE1B, grade: BLUEGRADE, note: 'Sphere unravels into slow fading bands and mist',
    layers: [
      ...[0, 1, 2].map((k) => slashBand(`Unravel${k + 1}`, { position: [0, 3.4, 0], rotation: BANDS[k + 2], spin: 260, spawns: [k * 0.08], life: 0.65, color: '#7c90f0', brightness: 1.2, size: [[0, 14], [1, 19]], transparency: [[0, 0.3], [1, 1]] })),
      mesh('Haze', 'Fading sphere haze', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#4a5cd8', brightness: 0.9, position: [0, 3.2, 0], spin: 120, spawns: [0], life: 0.8, size: [[0, 12], [1, 16]], transparency: [[0, 0.4], [1, 1]], scroll: [0.2, 0] }),
      { name: 'Mist', ref: 'Blue mist spreading low', position: [0, 2, 0], part: { Size: [8, 2, 8] }, emits: [[0, 14]],
        props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [80, 80], Speed: [4, 9], Drag: 1.5, Lifetime: [0.8, 1.0], Rotation: [0, 360], Size: [[0, 6], [1, 13, 2]], Color: [[0, '#5a74e8'], [1, '#22308a']], LightEmission: 0.25, Transparency: [[0, 0.4], [1, 1]], ZOffset: -2 } },
    ],
  });

  G.VFX_EFFECTS.CosmicStrike = compose({ name: 'CosmicStrike', version: 3, stage: STAGE1B, duration: 2.5, grade: BLUEGRADE,
    note: 'Video 1: cosmic combo on ForceField meshes, one dominant element per beat' }, [
    { part: 'CosmicAura', t: 0, scale: 0.8, label: '0.00 aura' },
    { part: 'FlatSlash', t: 0.1, label: '0.10 flat disc + ink' },
    { part: 'SmallOrb', t: 0.2, label: '0.20 swirl orb' },
    { part: 'InkHooks', t: 0.22, label: '0.22 ink hooks' },
    { part: 'PillarFlash', t: 0.32, label: '0.32 cylinder flash' },
    { part: 'SpikeCrown', t: 0.38, label: '0.38 spike crown' },
    { part: 'RiftTear', t: 0.45, label: '0.45 rift' },
    { part: 'CosmicSphere', t: 0.52, label: '0.52 hero sphere' },
    { part: 'StarFlash', t: 0.98, scale: 0.6, label: '0.98 star' },
    { part: 'Dissolve', t: 1.4, label: '1.40 dissolve' },
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
  // Camera close behind-right, swordsman facing screen-left; one dominant element per beat.
  const STAGE3 = { env: 'stone', bloom: [0.75, 0.85], camera: [6, 7.5, 10.5], target: [-1.2, 2.4, 0], dummy: { pos: [0, 0, 0], face: [-10, 0, -3], sword: 'katana' },
    swing: [[0, -40], [0.06, 140], [0.13, 140], [0.18, -40], [0.38, -40], [0.42, 150], [0.62, 150], [0.67, 30], [1.3, 30], [1.4, 120], [1.9, 120]] };
  const SHEET = { glow: { Color: '#d8e0e8', Transparency: 0.95 }, rim: { Color: '#6a727c', LightEmission: 0, Transparency: 0.7 }, mid: { Color: '#a4acb4', LightEmission: 0, Transparency: 0.4 }, core: { Color: '#e8ecf0', LightEmission: 0.3, Transparency: 0.7 } };
  const TOCAM = [-22, 34, 0];   // plane facing this stage's camera
  part({
    name: 'BladeGlint', previewAt: [-2, 4, 0], duration: 0.25, stage: STAGE3, note: 'Lens glint on the blade',
    layers: [{ name: 'Glint', ref: 'Blade glint', position: [0, 0, 0], emits: [[0, 1]],
      props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 2], [0.3, 4.5], [1, 2.5]], Color: '#ffffff', LightEmission: 1, Brightness: 1.8, ZOffset: 3 } }],
  });
  part({
    name: 'InkSpray', previewAt: [-2.4, 3, 1], duration: 0.3, stage: STAGE3, note: 'Black smudgy spike spray behind the cut',
    layers: [{ name: 'Spray', ref: 'Black smudge spikes', position: [0, 0, 0], emits: [[0, 1]],
      props: { Texture: 'ink_smudge', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.26, 0.26], Rotation: [0, 0], Size: [[0, 10], [1, 13]], Color: '#05050a', LightEmission: 0, Transparency: [[0, 0.05], [1, 0.3]], ZOffset: 0.5 } }],
  });
  part({
    name: 'WindSheet', previewAt: [-0.6, 3.2, 0], duration: 0.45, stage: STAGE3, note: 'Broad translucent grey afterimage sheet of the cut',
    shakes: [{ t: 0.02, dur: 0.15, amp: 0.2, freq: 28 }],
    layers: [mesh('Sheet', 'Translucent grey afterimage sheet (Ink mesh band sweeping with the blade)', { mesh: 'band', meshArgs: { arc: 160, inner: 0.12, cone: 0.1 }, texture: 'm_wind', material: 'Ink', color: '#9aa2ac', position: [0, 0, 0], rotation: [-10, 0, 62], spin: [[0, -70], [0.25, 25, 'out'], [1, 40]], spawns: [0], life: 0.42, size: [[0, 9], [0.25, 11.5, 'out'], [1, 12]], transparency: [[0, 0.1], [0.5, 0.3], [1, 1]] })],
  });
  part({
    name: 'DustKick', previewAt: [0, 0.8, 0], duration: 1.3, stage: STAGE3, note: 'Brown dust kicked up at the feet',
    layers: [{ name: 'Dust', ref: 'Dust', position: [0, 0, 0], part: { Size: [3, 0.3, 3] }, emits: [[0, 10]],
      props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [70, 70], Speed: [4, 9], Drag: 2.5, Lifetime: [0.8, 1.2], Rotation: [0, 360], Size: [[0, 3.5], [1, 8.5, 1.5]], Color: '#8c7c6a', LightEmission: 0, LightInfluence: 0.6, Transparency: [[0, 0.2], [1, 1]], ZOffset: -1 } }],
  });
  part({
    name: 'HeavyRing', previewAt: [-1.6, 3.3, 0], duration: 0.6, stage: STAGE3, note: 'Big dark motion-blurred ring slash with white highlight streaks and a glint',
    shakes: [{ t: 0.02, dur: 0.2, amp: 0.3, freq: 28 }],
    layers: [
      mesh('RingDark', 'Motion-blurred dark ring (Ink mesh, spinning)', { mesh: 'band', meshArgs: { arc: 360, inner: 0.38 }, texture: 'm_ringblur', material: 'Ink', color: '#0c0d10', position: [0, 0, 0], rotation: G.VFXSpec.faceRot([7.2, 5.1, 10.5]), spin: -1100, spawns: [0], life: 0.42, size: [[0, 9], [0.2, 12.5, 'out'], [1, 13.5]], transparency: [[0, 0], [0.6, 0.2], [1, 1]] }),
      mesh('RingLight', 'White highlight streaks on the ring (ForceField)', { mesh: 'band', meshArgs: { arc: 360, inner: 0.38 }, texture: 'm_ringhi', material: 'ForceField', color: '#ffffff', brightness: 1.6, fresnel: 0, position: [0, 0, 0], rotation: G.VFXSpec.faceRot([7.2, 5.1, 10.5]), spin: -1300, spawns: [0], life: 0.4, size: [[0, 9], [0.2, 12.4, 'out'], [1, 13.4]], transparency: [[0, 0], [0.6, 0.3], [1, 1]] }),
      { name: 'RingGlint', ref: 'Glint at the bottom of the ring', position: [-0.8, -4.4, 2.6], emits: [[0.06, 1]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 3], [0.3, 6], [1, 3.5]], Color: '#ffffff', LightEmission: 1, Brightness: 3, ZOffset: 3 } },
    ],
  });
  part({
    name: 'FireFlash', previewAt: [3.2, 3.6, -1.5], duration: 1.0, stage: STAGE3, note: 'Huge orange-white flash on the right, light column, pale ribbon, orange haze, embers',
    lights: [{ name: 'Fire', position: [0, 0, 0], Color: '#ff8a30', Range: 34, Brightness: [[0, 0], [0.01, 6], [0.15, 4.5], [0.6, 1.5], [1.0, 0]] }],
    impactFrames: [{ t: 0, dur: 0.034, Brightness: 0.35, Contrast: 0.2, Saturation: 0.2, TintColor: '#fff0e0' }],
    shakes: [{ t: 0.01, dur: 0.4, amp: 0.8, freq: 24 }],
    layers: [
      ...planeStack('Burst', 'Radial fire burst', { tex: 'fire_burst', facing: 'FacingCamera', emits: [[0, 1]], life: 0.5, size: 20, z: 1,
        colors: { glow: { Color: '#ff5a10', Transparency: 0.45 }, rim: { Color: '#d03008', LightEmission: 0.5 }, mid: { Color: '#ff8a24', LightEmission: 0.6 }, core: { Color: '#fff2d8', LightEmission: 1, Brightness: 1.6 } } }),
      { name: 'Column', ref: 'Tall light column', position: [0.6, 9, -0.5], emits: [[0, 1]],
        props: { Texture: 'light_column', Orientation: 'FacingCameraWorldUp', Speed: [0, 0], Lifetime: [0.32, 0.32], Rotation: [0, 0], Size: [[0, 18], [0.2, 26], [1, 24]], Color: '#ffa860', LightEmission: 1, Brightness: 1.5, Transparency: [[0, 0], [0.5, 0.2], [1, 1]], ZOffset: 1 } },
      ...planeStack('Ribbon', 'Pale flat swoosh ribbon', { tex: 'wind_sheet', dir: 'Back', pos: [-4.5, -1.2, 1.2], rot: [-10, 55, 0], emits: [[0.01, 1]], life: 0.35, size: 8, spin: 160,
        colors: { glow: { Color: '#ffffff', Transparency: 0.9 }, rim: { Color: '#8a8e94', LightEmission: 0, Transparency: 0.4 }, mid: { Color: '#e8eaee', LightEmission: 0.3, Transparency: 0.15 }, core: { Color: '#ffffff', LightEmission: 0.8 } } }),
      { name: 'Haze', ref: 'Orange haze hanging over the right side', position: [0.5, 0, 0], part: { Size: [6, 5, 3] }, emits: [[0.02, 6]], rate: [[0.05, 0.5, 10]],
        props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [1, 4], Lifetime: [0.7, 1.0], Rotation: [0, 360], Size: [[0, 8], [1, 14, 2]], Color: [[0, '#ff9a50'], [1, '#c8603a']], LightEmission: 0.6, Transparency: [[0, 0.55], [1, 1]], ZOffset: -1 } },
      { name: 'Embers', ref: 'Glowing ember dots and sparks', position: [0, 0, 0], part: { Size: [4, 4, 4] }, emits: [[0, 30]], rate: [[0.05, 0.6, 16]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [10, 34], Drag: 3, Acceleration: [0, -10, 0], Lifetime: [0.3, 0.45], Orientation: 'VelocityParallel', Size: [[0, 1.2, 0.4], [1, 0.3]], Color: [[0, '#fff2c0'], [0.4, '#ffa030'], [1, '#ff3a10']], LightEmission: 1, Brightness: 3 } },
      { name: 'EmberDots', ref: 'Hot ember dots', position: [0, 0, 0], part: { Size: [6, 5, 4] }, rate: [[0.05, 0.55, 14]],
        props: { Texture: 'bokeh', Shape: 'Box', Speed: [1, 4], Lifetime: [0.3, 0.45], Size: [[0, 0.5, 0.2], [0.3, 0.9, 0.3], [1, 0.2]], Color: '#ff7a30', LightEmission: 1, Brightness: 2.5 } },
    ],
  });
  part({
    name: 'RedPillar', previewAt: [0, 11, 0], duration: 0.5, stage: STAGE3, note: 'Wide red-orange light pillar dropping on the swordsman',
    lights: [{ name: 'Pillar', position: [0, -7, 0], Color: '#ff6040', Range: 24, Brightness: [[0, 0], [0.02, 4], [0.4, 0]] }],
    layers: [
      mesh('Pillar', 'Red ForceField cylinder pillar', { mesh: 'cylinder', texture: 'm_beam', material: 'ForceField', color: '#ff2a2a', brightness: 0.9, fresnel: 1.8, position: [0, 0, 0], spin: 300, spawns: [0], life: 0.45, size: [[0, [1, 24, 1]], [0.15, [4, 24, 4], 'out'], [1, [3, 24, 3]]], transparency: [[0, 0], [0.6, 0.2], [1, 1]], scroll: [0, -2.5] }),
      mesh('Core', 'Hot core', { mesh: 'cylinder', texture: 'm_solid', material: 'Neon', color: '#ff8070', brightness: 0.9, position: [0, 0, 0], spawns: [0], life: 0.4, size: [[0, [0.4, 24, 0.4]], [0.15, [1.6, 24, 1.6]], [1, [0.6, 24, 0.6]]], transparency: [[0, 0], [1, 1]] }),
    ],
  });
  G.VFX_EFFECTS.KatanaFlurry = compose({ name: 'KatanaFlurry', version: 3, stage: STAGE3, duration: 2.0, note: 'Video 3: katana combo, one dominant element per beat' }, [
    { part: 'BladeGlint', t: 0, at: [-2.6, 1.1, 0.8], label: '0.00 tip glint' },
    { part: 'DustKick', t: 0, at: [0, 0.6, 0], label: 'dust' },
    { part: 'BladeGlint', t: 0.07, at: [-0.4, 7.2, 0.3], scale: 1.2, tag: 'TopGlint', label: '0.07 glint (raised)' },
    { part: 'InkSpray', t: 0.13, at: [-2.6, 2.6, 2.2], label: '0.13 black spray' },
    { part: 'WindSheet', t: 0.13, at: [-0.6, 2.4, 0.8], label: '0.13 wind sheet' },
    { part: 'DustKick', t: 0.13, at: [-1, 0.6, 0.5], tag: 'Dust2', label: 'dust' },
    { part: 'BladeGlint', t: 0.2, at: [-4.8, 3.6, 1.6], scale: 1.5, tag: 'BigGlint', label: '0.20 big glint' },
    { part: 'HeavyRing', t: 0.4, at: [-2.4, 4.2, 2.0], label: '0.40 ring slash' },
    { part: 'FireFlash', t: 0.67, at: [3.4, 2.6, -1.2], label: '0.67 fire flash' },
    { part: 'RedPillar', t: 1.4, at: [0, 11, 0], label: '1.40 red pillar' },
  ]);
})(typeof window !== 'undefined' ? window : globalThis);
