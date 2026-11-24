// FireExplosion v2: ground fire blast. Hero = hand-drawn 16-drawing blast (on 2s) split into
// white glow/rim/mid/core flipbooks, then a cel smoke hero (on 3s) that takes over from the edges.
// Refs: Sukuna/Jogo flame blasts (JJK) for the crimson ink + black smoke, Wano-era One Piece for
// the impact star and saturated orange body.
(function (G) {
  const { stack, steps, flicker } = G.VFXSpec;
  const C = 4, BLAST = 38, SMOKE = 40;
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};
  G.VFX_EFFECTS.FireExplosion = {
    name: 'FireExplosion', version: 2, duration: 2.9,
    stage: { camera: [17, 8, 24], target: [0, 9, 0], dummy: { pos: [-11, 0, 8], face: [0, 0, 0] } },
    beats: [
      [0.0, 'Charge: lines pulled in, glint flickers'],
      [0.3, 'Impact frames: white, B/W, red'],
      [0.32, 'Flash star (4 drawings on 1s)'],
      [0.36, 'Blast blooms: lobes, tongues, core'],
      [0.75, 'Tips pinch off, embers rise, glints'],
      [1.0, 'Smoke eats in from the edges'],
      [1.7, 'Smoke breaks into round holes'],
    ],
    lights: [{ name: 'BlastLight', position: [0, C, 0], Color: '#ff8a30', Range: 52, Brightness: [[0, 0], [0.28, 1.5], [0.3, 9], [0.55, 5], [0.62, 6], [0.7, 4.5], [1.3, 1.4], [2.6, 0]] }],
    impactFrames: [
      { t: 0.3, dur: 0.034, Brightness: 0.75, Contrast: 0.2, Saturation: -0.3 },
      { t: 0.334, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, Void: '#000000', Highlight: { FillColor: '#ffffff' } },
      { t: 0.384, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, TintColor: '#ff2020', Void: '#000000', Highlight: { FillColor: '#000000' } },
    ],
    shakes: [{ t: 0.3, dur: 0.6, amp: 1.0, freq: 24 }],

    layers: [
      // ---------- charge ----------
      {
        name: 'GatherLines', role: 'Charge', ref: 'Energy sucked in before release',
        position: [0, C, 0], part: { Size: [26, 26, 26] }, rate: [[0, 0.26, 130]],
        props: {
          Texture: 'speedline', Shape: 'Sphere', ShapeStyle: 'Surface', ShapeInOut: 'Inward',
          Speed: [48, 60], Lifetime: [0.2, 0.24], Orientation: 'VelocityParallel',
          Size: [[0, 0], [0.25, 7, 1.5], [1, 3]], Transparency: [[0, 0.2], [1, 0]],
          Color: [[0, '#ffb347'], [1, '#fff6d8']], LightEmission: 1, Brightness: 2.2,
        },
      },
      {
        name: 'ChargeGlint', role: 'Charge', ref: 'Flickering 4-point glint, redrawn at 24 fps',
        position: [0, C, 0], emits: [[0, 1]],
        props: {
          Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [24, 24],
          Speed: [0, 0], Lifetime: [0.3, 0.3], Rotation: [0, 0], Size: [[0, 2], [0.8, 7], [1, 10]],
          Color: '#fff1c0', LightEmission: 1, Brightness: 2.5, ZOffset: 3,
        },
      },

      // ---------- impact ----------
      ...stack({
        name: 'Flash', role: 'Impact', ref: 'One Piece impact star, 4 drawings on 1s',
        position: [0, C, 0], emits: [[0.3, 1]],
        props: { Texture: 'fx_flash', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.2, 0.2], Rotation: [0, 0], Size: 30, ZOffset: 4 },
      }, {
        glow: { Color: '#ffb040', Transparency: 0.35 }, rim: { Color: '#ff6a10' }, mid: { Color: '#ffe68a' }, core: { Color: '#ffffff', Brightness: 2.5 },
      }),
      {
        name: 'ImpactLines', role: 'Impact', ref: 'Radial speed lines on the hit',
        position: [0, C, 0], part: { Size: [3, 3, 3] }, emits: [[0.3, 34]],
        props: {
          Texture: 'speedline', Shape: 'Sphere', ShapeStyle: 'Surface', ShapePartial: 0.7, Speed: [150, 210], Lifetime: [0.12, 0.18],
          Orientation: 'VelocityParallel', Size: [[0, 5], [1, 11, 2]], Transparency: [[0, 0], [0.7, 0], [1, 1]],
          Color: '#fff8e0', LightEmission: 1, Brightness: 2.5, ZOffset: 1,
        },
      },
      {
        name: 'Shockwave', role: 'Impact', ref: 'Ground ring, thins and breaks over 4 drawings',
        position: [0, 0.25, 0], emits: [[0.31, 1]],
        props: {
          Texture: 'ring', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Orientation: 'VelocityPerpendicular',
          EmissionDirection: 'Top', Speed: [0.01, 0.01], Lifetime: [0.34, 0.34], Size: [[0, 8], [0.4, 40], [1, 52]],
          Transparency: [[0, 0], [0.6, 0.15], [1, 1]], Color: '#ffe2a0', LightEmission: 0.5, Brightness: 1.4,
        },
      },

      // ---------- hero blast (4 stacked white layers) ----------
      ...stack({
        name: 'Blast', role: 'Blast (hero)', ref: '16 drawings on 2s: lobes, tongues, pinch-off, breakup',
        position: [0, BLAST * 0.45, 0], emits: [[0.33, 1]],
        props: {
          Texture: 'fx_blast', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Orientation: 'FacingCameraWorldUp',
          Speed: [0, 0], Lifetime: [1.34, 1.34], Rotation: [0, 0], Size: BLAST, ZOffset: 0,
        },
      }, {
        glow: { Color: '#ff6a1a', Transparency: steps(flicker(0.45, 0.12, 9, 3), 1) },
        rim: { Color: '#6a0905' },
        mid: { Color: [[0, '#ff9a1e'], [0.5, '#ff7414'], [1, '#e2480e']] },
        core: { Color: [[0, '#ffffff'], [0.4, '#fff2b8'], [1, '#ffd060']], Transparency: steps(flicker(0.05, 0.08, 9, 7)), Brightness: 1.8 },
      }),
      {
        name: 'FlameLicks', role: 'Blast (hero)', ref: 'Loose tongues thrown up off the dome, boiling at 12 fps',
        position: [0, 6, 0], part: { Size: [16, 4, 16] }, emits: [[0.36, 10]], rate: [[0.4, 0.9, 16]],
        props: {
          Texture: 'flame_lick', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [12, 12],
          Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [30, 30], Speed: [14, 24], Drag: 3, Acceleration: [0, 8, 0],
          Orientation: 'VelocityParallel', Lifetime: [0.35, 0.55], Size: [[0, 2], [0.25, 6, 1.5], [1, 0]],
          Color: [[0, '#fff0a0'], [0.4, '#ffa020'], [1, '#e03a0a']], LightEmission: 0.3, Brightness: 1.3, ZOffset: 0.3,
        },
      },

      // ---------- smoke hero ----------
      ...stack({
        name: 'Smoke', role: 'Smoke (hero)', ref: 'Cel lobes with crease lines, dissolves through round holes (on 3s)',
        position: [0, SMOKE * 0.3, 0], emits: [[0.8, 1]],
        props: {
          Texture: 'fx_smoke', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Orientation: 'FacingCameraWorldUp',
          Speed: [0, 0], Lifetime: [2.0, 2.0], Rotation: [0, 0], Size: SMOKE, ZOffset: -3,
          Transparency: [[0, 0], [0.72, 0], [0.9, 1], [1, 1]],
        },
      }, {
        glow: { Color: '#ff5a1a', Transparency: [[0, 0.45], [0.3, 0.7], [1, 1]] },
        rim: { Color: '#140d12' },
        mid: { Color: [[0, '#5e403e'], [0.3, '#3c3346'], [1, '#352e3e']] },
        core: { Color: [[0, '#b07458'], [0.3, '#675a74'], [1, '#5a4f66']], LightEmission: 0, Brightness: 1 },
      }),
      {
        name: 'GroundDust', role: 'Smoke (hero)', ref: 'Low dust skirt pushed out by the shockwave',
        position: [0, 1.2, 0], part: { Size: [6, 1, 6] }, emits: [[0.34, 14]],
        props: {
          Texture: 'puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Cylinder', ShapeStyle: 'Surface',
          Speed: [28, 40], Drag: 4, Acceleration: [0, 2, 0], Lifetime: [0.9, 1.3], Rotation: [-20, 20],
          Size: [[0, 4], [0.3, 8, 1.5], [1, 10, 2]], Color: [[0, '#d8a080'], [1, '#5e5464']], ZOffset: -1,
        },
      },

      // ---------- life: embers, glints, debris, scorch ----------
      {
        name: 'Embers', role: 'Life', ref: 'Needle sparks thrown out, then a steady rising trickle',
        position: [0, C, 0], part: { Size: [6, 6, 6] }, emits: [[0.3, 50]], rate: [[0.45, 1.6, 26]],
        props: {
          Texture: 'spark', Shape: 'Sphere', ShapePartial: 0.8, Speed: [22, 64], Drag: 2.2, Acceleration: [0, -20, 0],
          Lifetime: [0.4, 1.1], Orientation: 'VelocityParallel', Size: [[0, 1.4, 0.4], [1, 0.2]],
          Color: [[0, '#fff3b0'], [0.4, '#ffb030'], [1, '#ff4010']], LightEmission: 1, Brightness: 3,
        },
      },
      {
        name: 'Glints', role: 'Life', ref: 'Twinkles popping inside the fire (3 drawings each)',
        position: [0, 10, 0], part: { Size: [20, 14, 14] }, rate: [[0.36, 1.25, 9]],
        props: {
          Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.16, 0.22],
          Rotation: [0, 0], Size: [[0, 2.5, 1], [1, 2.5, 1]], Color: '#fff4cc', LightEmission: 1, Brightness: 2.5, ZOffset: 4,
        },
      },
      {
        name: 'Debris', role: 'Life', ref: 'Faceted chunks on ballistic arcs',
        position: [0, 0.4, 0], part: { Size: [4, 0.2, 4] }, emits: [[0.34, 16]],
        props: {
          Texture: 'rock', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [50, 50],
          Speed: [30, 46], Acceleration: [0, -95, 0], Lifetime: [0.72, 0.82],
          Rotation: [0, 360], RotSpeed: [-500, 500], Size: [[0, 1.4, 0.5], [1, 1.2, 0.4]],
          Color: '#7a6460', Transparency: [[0, 0], [0.9, 0], [1, 1]], LightInfluence: 1, Brightness: 1.4,
        },
      },
      {
        name: 'Scorch', role: 'Life', ref: 'Burnt crater decal',
        position: [0, 0.1, 0], emits: [[0.33, 1]],
        props: {
          Texture: 'scorch', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [2.5, 2.5], Rotation: [0, 0], Size: [[0, 12], [0.04, 20], [1, 20]],
          Color: '#0c0808', Transparency: [[0, 0.1], [0.8, 0.1], [1, 1]],
        },
      },
      {
        name: 'CrackGlow', role: 'Life', ref: 'Molten cracks cooling with a stepped flicker',
        position: [0, 0.14, 0], emits: [[0.33, 1]],
        props: {
          Texture: 'crack_glow', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [1.7, 1.7], Rotation: [0, 0], Size: [[0, 12], [0.06, 20], [1, 20]],
          Transparency: steps([0, 0.15, 0.05, 0.25, 0.1, 0.35, 0.3, 0.55, 0.7], 1), Color: [[0, '#fff2b0'], [0.3, '#ff8a20'], [1, '#c03010']],
          LightEmission: 1, Brightness: 2,
        },
      },
    ],
  };
})(typeof window !== 'undefined' ? window : globalThis);
