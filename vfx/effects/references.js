// Recreations of the three reference clips (Roblox battlegrounds-style VFX).
//   AzureTempest  - video 1: blue/white energy sphere of strand arcs, black ink crescents,
//                   navy serrated blades, star flash, crossing lines, bubbles, mist, bokeh.
//   FireworkBurst - video 2: white-hot pink impact, pink beam, cyan/pink shards, gold flares,
//                   pink/purple + gold firework spheres, ground ring, embers, haze.
//   KatanaFlurry  - video 3: blade glint, wind slash trails, black spike burst, dust,
//                   vortex ring slash, orange fire flash, fire beam, embers.
// Heroes are 4 stacked white layers (glow/rim/mid/core) with FIXED rotations so the layers align.
(function (G) {
  const { stack, steps, flicker } = G.VFXSpec;
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};

  // a stacked crescent/blade on a fixed plane (rotation = part CFrame.Angles, degrees)
  function planeStack(name, role, ref, o) {
    return stack({
      name, role, ref, position: o.pos, rotation: o.rot, emits: o.emits,
      props: {
        Texture: o.tex, FlipbookLayout: o.grid || 'Grid4x4', FlipbookMode: 'OneShot', Orientation: o.facing || 'VelocityPerpendicular',
        EmissionDirection: o.dir || 'Top', Speed: [0.01, 0.01], Lifetime: [o.life, o.life], Rotation: [o.spin || 0, o.spin || 0],
        RotSpeed: [o.rs || 0, o.rs || 0], Size: o.size, ZOffset: o.z || 0,
      },
    }, o.colors);
  }
  const ENERGY = (alpha) => ({
    glow: { Color: '#2340ff', Transparency: steps([0.55, 0.45, 0.58, 0.5, 0.6, 0.7, 0.82, 0.92], 1), Brightness: 1 },
    rim: { Color: '#141c8a', LightEmission: 0.2, Transparency: 0.2 + (alpha || 0) },
    mid: { Color: [[0, '#7e9aff'], [0.5, '#4e6cff'], [1, '#2c3ccc']], LightEmission: 0.35, Brightness: 1, Transparency: 0.05 + (alpha || 0) },
    core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.7, Transparency: steps(flicker(0.05, 0.08, 8, 3)) },
  });
  // plane normals clustered toward the camera (normal = +Z rotated by [rx, ry]); in-plane angle via spin
  const FACE = (k) => [((k * 37) % 50) - 25, 34 + ((k * 53) % 36) - 18, 0];
  // deterministic pseudo-random plane orientations
  const ORI = (k) => [((k * 73) % 180) - 90, (k * 131) % 360, ((k * 47) % 140) - 70];

  // ===================================================================================
  // 1. AzureTempest
  // ===================================================================================
  const C = [0, 3.6, 0];
  const az = [
    {
      name: 'BaseMist', role: 'Atmosphere', ref: 'Blue mist pooling and rolling out at the feet',
      position: [0, 0.8, 0], part: { Size: [9, 0.2, 9] }, rate: [[0, 1.5, 34]], emits: [[0.32, 14]],
      props: {
        Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [75, 75],
        Speed: [3, 9], Drag: 1.5, Lifetime: [0.9, 1.4], Rotation: [0, 360], RotSpeed: [-30, 30], Size: [[0, 4], [1, 10, 2]],
        Color: [[0, '#5a74e8'], [1, '#22308a']], LightEmission: 0.25, Brightness: 1, Transparency: [[0, 0.45], [0.6, 0.65], [1, 1]], ZOffset: -2,
      },
    },
    ...planeStack('GroundSwirl', 'Atmosphere', 'Spiral vortex swirling on the ground', {
      tex: 'swirl_disk', pos: [0, 0.35, 0], rot: [0, 0, 0], emits: [[0, 1], [0.62, 1]], life: 1.0, size: 19, rs: 140,
      colors: { glow: { Color: '#2a44ff', Transparency: 0.6 }, rim: { Color: '#141c8a', LightEmission: 0.2, Transparency: 0.5 }, mid: { Color: '#6a86ff', LightEmission: 0.5, Transparency: 0.15 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } },
    }),
    ...[0, 1, 2].flatMap((k) => planeStack(`ChargeArc${k + 1}`, 'Charge', 'Small strand arcs wrapping the character while charging', {
      tex: 'wisp_arc', dir: 'Back', pos: C, rot: FACE(k + 11), emits: [[0.02 + k * 0.07, 1]], life: 0.55, size: 8, spin: k * 120, colors: ENERGY(0.1),
    })),
    {
      name: 'Bokeh', role: 'Atmosphere', ref: 'Soft glowing dots drifting through the energy',
      position: C, part: { Size: [14, 9, 14] }, rate: [[0, 1.6, 26]], emits: [[0.3, 16]],
      props: {
        Texture: 'bokeh', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [180, 180], Speed: [1, 5], Drag: 1, Lifetime: [0.4, 0.9],
        Size: [[0, 0.3, 0.2], [0.3, 1.1, 0.4], [1, 0.2]], Color: '#c4d2ff', LightEmission: 1, Brightness: 2.2, ZOffset: 2,
      },
    },
    // ---- burst ----
    ...planeStack('StarFlash', 'Burst', 'Navy 4-point star with a white rim on the hit', {
      tex: 'star4', grid: 'Grid2x2', pos: C, rot: [0, 0, 0], facing: 'FacingCamera', emits: [[0.28, 1]], life: 0.24, size: 13, z: 3,
      colors: { glow: { Color: '#3a5cff', Transparency: 0.3 }, rim: { Color: '#f0f4ff', LightEmission: 0.6, Brightness: 1.6 }, mid: { Color: '#0c1660', LightEmission: 0 }, core: { Color: '#eaff7a', LightEmission: 1, Brightness: 2 } },
    }),
    ...[0, 1, 2, 3, 4, 5].flatMap((k) => planeStack(`EnergyArc${k + 1}`, 'Burst', 'Strand crescents wrapping the sphere in many planes', {
      tex: 'wisp_arc', dir: 'Back', pos: C, rot: FACE(k + 1), emits: [[0.3 + k * 0.045, 1]], life: 0.62, size: 13 + (k % 3) * 2.5, spin: k * 61, colors: ENERGY(),
    })),
    {
      name: 'InkArcs', role: 'Burst', ref: 'Black calligraphic crescents interleaved with the light',
      position: C, rotation: [0, 32, 0], part: { Size: [1, 1, 1] }, emits: [[0.31, 3], [0.46, 2], [0.62, 2]],
      props: {
        Texture: 'ink_arc', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', EmissionDirection: 'Back', SpreadAngle: [40, 40], Orientation: 'VelocityPerpendicular',
        Speed: [0.01, 0.01], Lifetime: [0.42, 0.5], Rotation: [0, 360], Size: [[0, 13, 2.5], [1, 15, 2.5]], Color: '#030408', LightEmission: 0, ZOffset: 1,
      },
    },
    ...[0, 1, 2].flatMap((k) => planeStack(`SawBlade${k + 1}`, 'Burst', 'Navy serrated blades with white comb teeth and screentone', {
      tex: 'saw_fan', dir: 'Back', pos: C, rot: FACE(k + 21), emits: [[0.36 + k * 0.08, 1]], life: 0.5, size: 13, spin: 40 + k * 110, z: 0.5,
      colors: { glow: { Color: '#3050ff', Transparency: 0.55 }, rim: { Color: '#e6ecff', LightEmission: 0.5, Brightness: 1.4 }, mid: { Color: '#0e1a78', LightEmission: 0 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 2 } },
    })),
    {
      name: 'InkLines', role: 'Burst', ref: 'Long black lines cutting through the sphere',
      position: C, part: { Size: [1, 1, 1] }, emits: [[0.31, 3], [0.52, 3]],
      props: {
        Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01],
        Lifetime: [0.22, 0.34], Size: [[0, 14], [0.2, 24, 3], [1, 22, 3]], Color: '#04050a', LightEmission: 0, ZOffset: 1.2,
      },
    },
    {
      name: 'LightLines', role: 'Burst', ref: 'Thin white lines with glow',
      position: C, part: { Size: [1, 1, 1] }, emits: [[0.33, 3], [0.56, 2]],
      props: {
        Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', Orientation: 'VelocityParallel', Speed: [0.01, 0.01],
        Lifetime: [0.2, 0.3], Size: [[0, 12], [0.2, 20, 3], [1, 18, 3]], Color: '#e8f0ff', LightEmission: 1, Brightness: 2.5, ZOffset: 1.3,
      },
    },
    {
      name: 'Flecks', role: 'Burst', ref: 'Yellow-green accent flecks and white sparks',
      position: C, part: { Size: [5, 5, 5] }, emits: [[0.3, 26]], rate: [[0.35, 1.0, 22]],
      props: {
        Texture: 'spark', Shape: 'Sphere', Speed: [16, 40], Drag: 4, Lifetime: [0.25, 0.55], Orientation: 'VelocityParallel',
        Size: [[0, 1.4, 0.5], [1, 0.3]], Color: [[0, '#ffffff'], [0.3, '#e6ff70'], [1, '#7aa0ff']], LightEmission: 1, Brightness: 2.5, ZOffset: 2,
      },
    },
    {
      name: 'MistBurst', role: 'Burst', ref: 'Blue mist blown out by the burst',
      position: C, part: { Size: [4, 4, 4] }, emits: [[0.32, 12]],
      props: {
        Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Sphere', Speed: [10, 18], Drag: 3, Lifetime: [0.8, 1.2],
        Rotation: [0, 360], Size: [[0, 5], [1, 11, 2]], Color: [[0, '#5a70d8'], [1, '#22308a']], LightEmission: 0.2, Transparency: [[0, 0.4], [1, 1]], ZOffset: -1.5,
      },
    },
    ...planeStack('Bubbles', 'Aftermath', 'Glassy energy bubbles swelling and popping', {
      tex: 'blobs', pos: [0, 3.2, 0], rot: [0, 0, 0], facing: 'FacingCamera', emits: [[0.78, 1]], life: 0.85, size: 13, z: 1,
      colors: { glow: { Color: '#2a44ff', Transparency: 0.75 }, rim: { Color: '#c8d4ff', LightEmission: 0.6, Brightness: 1.1 }, mid: { Color: '#3a54d0', LightEmission: 0.15, Transparency: 0.55 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } },
    }),
    ...[0, 1].flatMap((k) => planeStack(`AfterArc${k + 1}`, 'Aftermath', 'Late strand arcs swirling around the bubbles', {
      tex: 'wisp_arc', dir: 'Back', pos: C, rot: FACE(k + 31), emits: [[0.8 + k * 0.08, 1]], life: 0.6, size: 15, spin: 200 + k * 90, colors: ENERGY(0.15),
    })),
  ];
  G.VFX_EFFECTS.AzureTempest = {
    name: 'AzureTempest', version: 1, duration: 2.4,
    stage: { env: 'sky', bloom: [0.6, 0.9], camera: [13, 6.5, 17], target: [0, 3.6, 0], dummy: { pos: [0, 0, 0], face: [0, 0, 10] } },
    beats: [[0, 'Charge: swirl, mist, small arcs'], [0.28, 'Star flash + blue impact frame'], [0.3, 'Sphere of strand arcs, ink crescents, blades, lines'], [0.78, 'Bubbles swell, late arcs'], [1.2, 'Mist and bokeh settle']],
    lights: [{ name: 'AzureLight', position: C, Color: '#5a78ff', Range: 34, Brightness: [[0, 0.5], [0.27, 1.5], [0.3, 6], [0.4, 3.5], [0.48, 4.6], [0.6, 3], [0.8, 3.6], [1.2, 1.2], [1.8, 0]] }],
    impactFrames: [{ t: 0.28, dur: 0.034, Brightness: 0.3, Contrast: 0.4, Saturation: 0.3, TintColor: '#b8c8ff' }],
    shakes: [{ t: 0.3, dur: 0.45, amp: 0.55, freq: 26 }],
    layers: az,
  };

  // ===================================================================================
  // 2. FireworkBurst
  // ===================================================================================
  const H = [0, 5.5, 0], FA = [-11, 14, -6], FB = [12, 15, -8];
  const firework = (tag, at, t, cols, n) => [
    {
      name: `${tag}Flare`, role: `Firework ${tag}`, ref: 'Sun-like flare before the shell bursts',
      position: at, emits: [[t - 0.1, 1]],
      props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.42, 0.42], Rotation: [0, 0], Size: [[0, 5], [0.3, 13], [1, 7]], Color: cols[0], LightEmission: 1, Brightness: 1.5, Transparency: [[0, 0], [0.6, 0.2], [1, 1]] },
    },
    {
      name: `${tag}Streaks`, role: `Firework ${tag}`, ref: 'Shell bursts: streaks shoot out on a sphere',
      position: at, part: { Size: [1, 1, 1] }, emits: [[t, n]],
      props: {
        Texture: 'spark', Shape: 'Sphere', ShapeStyle: 'Surface', Speed: [30, 38], Drag: 2.6, Lifetime: [0.35, 0.5], Orientation: 'VelocityParallel',
        Size: [[0, 2.2, 0.4], [1, 0.8]], Color: [[0, '#ffffff'], [1, cols[1]]], LightEmission: 1, Brightness: 3,
      },
    },
    {
      name: `${tag}Dots`, role: `Firework ${tag}`, ref: 'Twinkling stars that drift down and fade',
      position: at, part: { Size: [1, 1, 1] }, emits: [[t, n]],
      props: {
        Texture: 'sparkle', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [14, 20], Shape: 'Sphere', ShapeStyle: 'Surface',
        Speed: [30, 38], Drag: 2.6, Acceleration: [0, -5, 0], Lifetime: [1.0, 1.7], Size: [[0, 0.9, 0.3], [1, 0.5, 0.2]],
        Color: [[0, '#ffffff'], [0.25, cols[1]], [1, cols[2]]], LightEmission: 1, Brightness: 2.6, Transparency: [[0, 0], [0.7, 0.2], [1, 1]],
      },
    },
  ];
  const fw = [
    {
      name: 'HitFlare', role: 'Impact', ref: 'White-hot flash with a lens flare on contact',
      position: H, emits: [[0.06, 1]],
      props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.3, 0.3], Rotation: [0, 0], Size: [[0, 6], [0.15, 11], [1, 8]], Color: '#ffe0f6', LightEmission: 1, Brightness: 1.6, Transparency: [[0, 0], [0.5, 0.15], [1, 1]], ZOffset: 3 },
    },
    ...[0, 1, 2].flatMap((k) => planeStack(`PinkArc${k + 1}`, 'Impact', 'White-pink strand crescents tearing through the hit', {
      tex: 'wisp_arc', dir: 'Back', pos: H, rot: [FACE(k + 41)[0], FACE(k + 41)[1] - 30, 0], emits: [[0.06 + k * 0.05, 1]], life: 0.5, size: 10 + k * 1.5, spin: k * 95,
      colors: {
        glow: { Color: '#ff3ad0', Transparency: steps([0.55, 0.45, 0.58, 0.65, 0.75, 0.85, 0.92, 1], 1), Brightness: 1 },
        rim: { Color: '#8a1880', LightEmission: 0.2, Transparency: 0.2 }, mid: { Color: [[0, '#ff9ef0'], [1, '#e050d0']], LightEmission: 0.45, Brightness: 1 },
        core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6, Transparency: 0.1 },
      },
    })),
    {
      name: 'PinkBeam', role: 'Impact', ref: 'Long diagonal pink beam through the target',
      position: H, rotation: [0, 0, -38], emits: [[0.08, 1]],
      props: { Texture: 'line', EmissionDirection: 'Top', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.4, 0.4], Size: [[0, 18], [0.12, 50], [1, 44]], Color: '#ff6ae4', LightEmission: 1, Brightness: 3, Transparency: [[0, 0], [0.5, 0.1], [1, 1]], ZOffset: 2 },
    },
    {
      name: 'CyanShards', role: 'Impact', ref: 'Cyan shard streaks blown out of the hit',
      position: H, part: { Size: [2, 2, 2] }, emits: [[0.07, 36]],
      props: { Texture: 'spark', Shape: 'Sphere', Speed: [40, 90], Drag: 5, Lifetime: [0.25, 0.5], Orientation: 'VelocityParallel', Size: [[0, 3, 1], [1, 0.4]], Color: [[0, '#ffffff'], [1, '#40e8ff']], LightEmission: 1, Brightness: 3 },
    },
    {
      name: 'PinkShards', role: 'Impact', ref: 'Pink and gold sparks',
      position: H, part: { Size: [2, 2, 2] }, emits: [[0.07, 50]], rate: [[0.1, 0.6, 40]],
      props: { Texture: 'spark', Shape: 'Sphere', Speed: [25, 70], Drag: 4, Acceleration: [0, -10, 0], Lifetime: [0.3, 0.7], Orientation: 'VelocityParallel', Size: [[0, 2, 0.8], [1, 0.3]], Color: [[0, '#ffffff'], [0.4, '#ff8ae6'], [1, '#ffb040']], LightEmission: 1, Brightness: 3 },
    },
    {
      name: 'HitGlints', role: 'Impact', ref: 'Glints popping around the impact',
      position: H, part: { Size: [9, 7, 9] }, rate: [[0.08, 0.7, 26]],
      props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [0, 0], Lifetime: [0.14, 0.22], Rotation: [0, 0], Size: [[0, 2.5, 1.2], [1, 2.5, 1.2]], Color: '#fff4ff', LightEmission: 1, Brightness: 2.6, ZOffset: 3 },
    },
    ...[0, 1].flatMap((k) => planeStack(`WindArc${k + 1}`, 'Impact', 'Pale wind arcs ringing the impact', {
      tex: 'trail_arc', pos: [0, 2.4, 0], rot: [k ? 8 : -6, k * 140, k ? -10 : 12], emits: [[0.1 + k * 0.06, 1]], life: 0.6, size: 16 + k * 3, spin: k * 150,
      colors: { glow: { Color: '#c8c8e0', Transparency: 0.7 }, rim: { Color: '#4a4a5c', LightEmission: 0, Transparency: 0.55 }, mid: { Color: '#e8e8f4', LightEmission: 0.4, Transparency: 0.35 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.8 } },
    })),
    ...planeStack('GroundRing', 'Impact', 'Shockwave swirl on the ground', {
      tex: 'swirl_disk', pos: [0, 0.3, 0], rot: [0, 0, 0], emits: [[0.08, 1]], life: 0.9, size: 18, rs: -90,
      colors: { glow: { Color: '#ffb0e0', Transparency: 0.7 }, rim: { Color: '#202028', LightEmission: 0, Transparency: 0.3 }, mid: { Color: '#d8d0e0', LightEmission: 0.3, Transparency: 0.25 }, core: { Color: '#ffffff', LightEmission: 1, Brightness: 1.6 } },
    }),
    {
      name: 'GroundEmbers', role: 'Aftermath', ref: 'Orange ember streaks skidding across the ground',
      position: [0, 0.5, 0], part: { Size: [6, 0.4, 6] }, emits: [[0.1, 30]],
      props: { Texture: 'spark', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [80, 80], Speed: [10, 26], Drag: 2.5, Acceleration: [0, -14, 0], Lifetime: [0.8, 1.8], Orientation: 'VelocityParallel', Size: [[0, 1.4, 0.4], [1, 0.4]], Color: [[0, '#ffd080'], [1, '#ff4a10']], LightEmission: 1, Brightness: 2.5 },
    },
    {
      name: 'Haze', role: 'Aftermath', ref: 'Grey smoke haze left behind',
      position: [0, 2.5, 0], part: { Size: [8, 3, 8] }, emits: [[0.12, 12]], rate: [[0.2, 1.2, 8]],
      props: { Texture: 'mist', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [2, 6], Lifetime: [1.2, 1.8], Rotation: [0, 360], Size: [[0, 6], [1, 13, 2]], Color: '#a8a4b4', LightEmission: 0.15, Transparency: [[0, 0.55], [1, 1]], ZOffset: -3 },
    },
    ...firework('A', FA, 0.34, ['#ffa8f0', '#ff70e0', '#7a68ff'], 200),
    ...firework('B', FB, 0.42, ['#ffcc70', '#ffc040', '#ff7a20'], 200),
  ];
  G.VFX_EFFECTS.FireworkBurst = {
    name: 'FireworkBurst', version: 1, duration: 3.0,
    stage: { env: 'night', bloom: [1.1, 0.7], camera: [3, 9, 30], target: [0, 8, -2], dummy: { pos: [1.5, 0, 1], face: [-10, 0, 10] } },
    beats: [[0.06, 'White-hot pink impact, beam, shards'], [0.24, 'Gold and pink flares'], [0.34, 'Pink firework bursts'], [0.42, 'Gold firework bursts'], [1.2, 'Stars drift and fade, embers skid']],
    lights: [{ name: 'HitLight', position: H, Color: '#ffb8f0', Range: 40, Brightness: [[0, 0], [0.05, 0], [0.07, 8], [0.3, 3], [0.6, 1], [1.4, 0]] }, { name: 'GoldLight', position: FB, Color: '#ffc060', Range: 50, Brightness: [[0, 0], [0.32, 0], [0.42, 5], [1.2, 1], [2.2, 0]] }],
    impactFrames: [{ t: 0.06, dur: 0.034, Brightness: 0.25, Contrast: 0.2, Saturation: 0.1, TintColor: '#ffe8fa' }],
    shakes: [{ t: 0.07, dur: 0.4, amp: 0.6, freq: 26 }],
    layers: fw,
  };

  // ===================================================================================
  // 3. KatanaFlurry
  // ===================================================================================
  const P1 = [0.8, 3.2, -2.2];
  const WIND = { glow: { Color: '#a8b8c8', Transparency: 0.88 }, rim: { Color: '#2c323e', LightEmission: 0, Transparency: 0.6 }, mid: { Color: '#a6b0bc', LightEmission: 0, Transparency: 0.5 }, core: { Color: '#ffffff', LightEmission: 0.8, Brightness: 1.1, Transparency: 0.4 } };
  const kf = [
    {
      name: 'TipGlint', role: 'Slash 1', ref: 'Lens glint on the blade tip before the draw',
      position: [2.4, 7.2, -1.2], emits: [[0, 1], [0.86, 1]],
      props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: [[0, 3], [0.3, 8], [1, 5]], Color: '#ffffff', LightEmission: 1, Brightness: 3, ZOffset: 3 },
    },
    ...planeStack('WindSlash1', 'Slash 1', 'Grey-white wind trail of the first cut', {
      tex: 'trail_arc', pos: P1, rot: [-55, 0, -30], emits: [[0.06, 1]], life: 0.45, size: 14, spin: 180, colors: WIND,
    }),
    {
      name: 'InkSpikes', role: 'Slash 1', ref: 'Black jagged spike burst behind the character',
      position: [0, 3.4, 0.6], emits: [[0.08, 1], [0.9, 1]],
      props: { Texture: 'ink_spikes', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.24, 0.24], Rotation: [0, 0], Size: [[0, 9], [1, 13]], Color: '#06060a', LightEmission: 0, Transparency: [[0, 0.05], [1, 0.4]], ZOffset: -2 },
    },
    {
      name: 'Dust', role: 'Slash 1', ref: 'Dust kicked up at the feet',
      position: [0, 0.8, 0], part: { Size: [3, 0.3, 3] }, emits: [[0.06, 8], [0.88, 8]],
      props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [70, 70], Speed: [5, 11], Drag: 2.5, Lifetime: [0.8, 1.2], Rotation: [0, 360], Size: [[0, 3], [1, 8, 1.5]], Color: '#8c7c6a', LightEmission: 0, LightInfluence: 0.6, Transparency: [[0, 0.2], [1, 1]], ZOffset: -1 },
    },
    ...planeStack('RingSlash', 'Slash 2', 'Dark vortex ring slash with white highlight strands', {
      tex: 'ring_slash', pos: [0.4, 3.4, -1.6], rot: [-80, 0, 0], emits: [[0.28, 1]], life: 0.65, size: 12, rs: -220,
      colors: { glow: { Color: '#8c9cb0', Transparency: 0.9 }, rim: { Color: '#06070a', LightEmission: 0, Transparency: 0.2 }, mid: { Color: '#3a404c', LightEmission: 0, Transparency: 0.35 }, core: { Color: '#ffffff', LightEmission: 0.9, Brightness: 1.2, Transparency: 0.3 } },
    }),
    {
      name: 'RingGlint', role: 'Slash 2', ref: 'Glint on the ring edge',
      position: [-3.6, 2.4, -2.4], emits: [[0.3, 1]],
      props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.18, 0.18], Rotation: [0, 0], Size: [[0, 3], [0.3, 7], [1, 4]], Color: '#ffffff', LightEmission: 1, Brightness: 3, ZOffset: 3 },
    },
    // ---- fire ----
    ...planeStack('FireFlash', 'Fire', 'Huge orange fire flash at the blade', {
      tex: 'fire_burst', pos: [3.6, 5.2, -1.6], rot: [0, 0, 0], facing: 'FacingCamera', emits: [[0.55, 1]], life: 0.55, size: 13, z: 1,
      colors: { glow: { Color: '#ff5a10', Transparency: 0.35, Brightness: 1.2 }, rim: { Color: '#c82a08', LightEmission: 0.5 }, mid: { Color: '#ff8a20', LightEmission: 0.7, Brightness: 1.1 }, core: { Color: '#fff2d0', LightEmission: 1, Brightness: 2 } },
    }),
    {
      name: 'FireFlare', role: 'Fire', ref: 'Orange lens flare over the flash',
      position: [3.6, 3.6, -1.6], emits: [[0.55, 1]],
      props: { Texture: 'flare', Speed: [0, 0], Lifetime: [0.3, 0.3], Rotation: [0, 0], Size: [[0, 8], [0.2, 16], [1, 10]], Color: '#ffa850', LightEmission: 1, Brightness: 1.6, Transparency: [[0, 0], [1, 1]], ZOffset: 3 },
    },
    {
      name: 'FireBeam', role: 'Fire', ref: 'Thin red-orange beam shooting up',
      position: [3.6, 3, -3], emits: [[0.6, 1]],
      props: { Texture: 'line', EmissionDirection: 'Top', Orientation: 'VelocityParallel', Speed: [0.01, 0.01], Lifetime: [0.36, 0.36], Size: [[0, 8], [0.2, 30], [1, 26]], Color: '#ff4a10', LightEmission: 1, Brightness: 1.4, Transparency: [[0, 0], [0.6, 0.2], [1, 1]], ZOffset: 2 },
    },
    {
      name: 'Embers', role: 'Fire', ref: 'Embers and orange sparks',
      position: [3.2, 3, -2.8], part: { Size: [3, 3, 3] }, emits: [[0.55, 40]], rate: [[0.6, 1.4, 18]],
      props: { Texture: 'spark', Shape: 'Sphere', Speed: [14, 46], Drag: 3, Acceleration: [0, -12, 0], Lifetime: [0.4, 1.0], Orientation: 'VelocityParallel', Size: [[0, 1.4, 0.5], [1, 0.3]], Color: [[0, '#fff2c0'], [0.4, '#ffa030'], [1, '#ff3a10']], LightEmission: 1, Brightness: 3 },
    },
    {
      name: 'FireSmoke', role: 'Fire', ref: 'Brown smoke rolling off the flash',
      position: [3.2, 2.5, -2.8], part: { Size: [4, 2, 4] }, emits: [[0.62, 8]],
      props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [60, 60], Speed: [3, 8], Lifetime: [0.9, 1.3], Rotation: [0, 360], Size: [[0, 5], [1, 11, 2]], Color: '#6a4a38', LightEmission: 0, Transparency: [[0, 0.3], [1, 1]], ZOffset: -1 },
    },
    // ---- second cut ----
    ...planeStack('WindSlash2', 'Slash 3', 'Second wind trail, opposite diagonal', {
      tex: 'trail_arc', pos: [0.4, 3.0, -2.0], rot: [-60, 0, 28], emits: [[0.9, 1]], life: 0.45, size: 15, spin: 20, colors: WIND,
    }),
  ];
  G.VFX_EFFECTS.KatanaFlurry = {
    name: 'KatanaFlurry', version: 1, duration: 2.2,
    stage: { env: 'sky', bloom: [0.9, 0.8], camera: [9, 5.5, -13], target: [0.8, 3.4, -1.5], dummy: { pos: [0, 0, 0], face: [0, 0, -10], sword: 'katana' },
      swing: [[0, 110], [0.05, 110], [0.1, -40], [0.28, -40], [0.32, 140], [0.5, 140], [0.55, 20], [0.85, 110], [0.9, -40], [1.4, -40]] },
    beats: [[0, 'Blade glint'], [0.06, 'Wind slash, ink spikes, dust'], [0.28, 'Vortex ring slash'], [0.55, 'Fire flash, beam, embers'], [0.9, 'Second cut']],
    lights: [{ name: 'FireLight', position: [3.6, 3.4, -1.6], Color: '#ff8a30', Range: 30, Brightness: [[0, 0], [0.53, 0], [0.56, 5], [0.7, 4], [1.1, 1], [1.6, 0]] }],
    impactFrames: [{ t: 0.55, dur: 0.034, Brightness: 0.3, Contrast: 0.3, Saturation: 0.2, TintColor: '#fff0e0' }],
    shakes: [{ t: 0.08, dur: 0.15, amp: 0.25, freq: 28 }, { t: 0.56, dur: 0.4, amp: 0.8, freq: 24 }],
    layers: kf,
  };
})(typeof window !== 'undefined' ? window : globalThis);
