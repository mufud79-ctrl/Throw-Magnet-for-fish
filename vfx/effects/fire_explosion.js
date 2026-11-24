// FireExplosion v1: anime fire blast (refs: Jogo's volcano / Sukuna's Fuga (JJK), Ace's Hiken (One Piece)).
// Every key under `props` is a real Roblox ParticleEmitter property; values use spec shorthand:
//   NumberSequence  -> [[time, value, envelope?], ...]    NumberRange -> [min, max]
//   ColorSequence   -> [[time, '#hex'], ...] or '#hex'      Vector2/3   -> [x, y] / [x, y, z]
// `position` = attachment offset from the effect origin (studs). `part.Size` = emitter part size,
// required for Shape-based emission (Sphere/Cylinder/Disc/Box). `emits` = [[time, count]] -> :Emit(count).
// `rate` = [[t0, t1, perSecond]] -> Enabled window.
(function (G) {
  const C = 4; // blast centre height
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};
  G.VFX_EFFECTS.FireExplosion = {
    name: 'FireExplosion',
    version: 1,
    duration: 2.6,
    beats: [
      [0.0, 'Anticipation: lines get sucked in, core charges'],
      [0.3, 'Impact frames: white, then B/W ink, then red'],
      [0.43, 'Fireball blooms; flame licks and shockwave'],
      [0.7, 'Hang: fire stalls (high Drag), embers arc'],
      [1.2, 'Erode: puffs dissolve into cel smoke'],
    ],
    lights: [
      { name: 'BlastLight', position: [0, C, 0], Color: '#ff8a30', Range: 48, Brightness: [[0, 0], [0.28, 1.5], [0.3, 9], [0.55, 5], [1.2, 1.2], [2.4, 0]] },
    ],
    impactFrames: [
      { t: 0.3, dur: 0.034, Brightness: 0.75, Contrast: 0.2, Saturation: -0.3 },
      { t: 0.334, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, Void: '#000000', Highlight: { FillColor: '#ffffff', FillTransparency: 0 } },
      { t: 0.384, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, TintColor: '#ff2020', Void: '#000000', Highlight: { FillColor: '#000000', FillTransparency: 0 } },
    ],
    shakes: [{ t: 0.3, dur: 0.55, amp: 0.9, freq: 24 }],

    layers: [
      // ---------- 1. Anticipation ----------
      {
        name: 'GatherLines', role: 'Anticipation', ref: 'Energy being pulled in before a JJK technique fires',
        position: [0, C, 0], part: { Size: [26, 26, 26] }, rate: [[0, 0.24, 140]],
        props: {
          Texture: 'speedline', Shape: 'Sphere', ShapeStyle: 'Surface', ShapeInOut: 'Inward',
          Speed: [48, 60], Lifetime: [0.2, 0.24], Orientation: 'VelocityParallel',
          Size: [[0, 0], [0.25, 7, 1.5], [1, 3]], Transparency: [[0, 0.2], [1, 0]],
          Color: [[0, '#ffb347'], [1, '#fff6d8']], LightEmission: 1, Brightness: 2.2,
        },
      },
      {
        name: 'ChargeCore', role: 'Anticipation', ref: 'Bright pin-point that swells before detonation',
        position: [0, C, 0], emits: [[0, 1]],
        props: {
          Texture: 'core_glow', Speed: [0, 0], Lifetime: [0.31, 0.31], ZOffset: 2,
          Size: [[0, 0.8], [0.7, 4.5], [0.85, 3], [1, 6.5]], Transparency: 0,
          LightEmission: 1, Brightness: 3,
        },
      },

      // ---------- 2. Detonation ----------
      {
        name: 'FlashStar', role: 'Detonation', ref: 'One Piece impact star / JJK black-flash spike burst',
        position: [0, C, 0], emits: [[0.3, 2]],
        props: {
          Texture: 'starburst', Speed: [0, 0], Lifetime: [0.2, 0.24], Rotation: [0, 360], RotSpeed: [-40, 40], ZOffset: 4,
          Size: [[0, 6], [0.15, 30, 4], [0.6, 26], [1, 8]], Transparency: [[0, 0], [0.55, 0], [1, 1]],
          LightEmission: 0.6, Brightness: 2.5,
        },
      },
      {
        name: 'ImpactLines', role: 'Detonation', ref: 'Radial speed lines on the impact frame',
        position: [0, C, 0], part: { Size: [3, 3, 3] }, emits: [[0.3, 36]],
        props: {
          Texture: 'speedline', Shape: 'Sphere', ShapeStyle: 'Surface', Speed: [150, 210], Lifetime: [0.12, 0.18],
          Orientation: 'VelocityParallel', Size: [[0, 5], [1, 11, 2]], Transparency: [[0, 0], [0.7, 0], [1, 1]],
          Color: '#fff8e0', LightEmission: 1, Brightness: 2.5, ZOffset: 1,
        },
      },
      {
        name: 'FireCore', role: 'Fireball', ref: 'Dense white-hot heart of the blast',
        position: [0, C, 0], part: { Size: [3, 3, 3] }, emits: [[0.3, 9]],
        props: {
          Texture: 'flame_puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot',
          Shape: 'Sphere', Speed: [2, 6], Drag: 4, Lifetime: [0.55, 0.75], Rotation: [0, 360], RotSpeed: [-30, 30],
          Size: [[0, 8], [0.15, 17, 2], [1, 19, 2]], Transparency: 0,
          Color: [[0, '#ffffff'], [0.5, '#fff0d0'], [1, '#ffb080']], LightEmission: 0.2, Brightness: 1.35, ZOffset: 1,
        },
      },
      {
        name: 'FireBurst', role: 'Fireball', ref: 'Cel-shaded fire billows thrown outward (Jogo volcano)',
        position: [0, C - 1, 0], part: { Size: [5, 5, 5] }, emits: [[0.3, 30]],
        props: {
          Texture: 'flame_puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot',
          Shape: 'Sphere', ShapeStyle: 'Volume', ShapePartial: 0.62, Speed: [24, 40], Drag: 5, Acceleration: [0, 14, 0],
          Lifetime: [0.55, 0.8], Rotation: [0, 360], RotSpeed: [-70, 70],
          Size: [[0, 5], [0.2, 12.5, 2.5], [1, 14, 2.5]], Transparency: 0,
          Color: [[0, '#ffffff'], [0.6, '#fff0dc'], [1, '#e0906a']], LightEmission: 0.12, Brightness: 1.2,
        },
      },
      {
        name: 'InkLicks', role: 'Fireball', ref: 'Dark crimson backing tongues give the hard anime outline',
        position: [0, C, 0], part: { Size: [3, 3, 3] }, emits: [[0.31, 16]],
        props: {
          Texture: 'ink_spike', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [12, 12],
          Shape: 'Sphere', ShapeStyle: 'Surface', ShapePartial: 0.5, Speed: [55, 70], Drag: 8,
          Orientation: 'VelocityParallel', Lifetime: [0.4, 0.55],
          Size: [[0, 5], [0.2, 16, 3], [1, 0]], Transparency: 0,
          LightEmission: 0, Brightness: 1, ZOffset: -1.5,
        },
      },
      {
        name: 'FlameLicks', role: 'Fireball', ref: 'Ace Hiken / Fuga flame tongues, boiling on 12fps',
        position: [0, C, 0], part: { Size: [3, 3, 3] }, emits: [[0.3, 24]],
        props: {
          Texture: 'flame_spike', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [12, 12],
          Shape: 'Sphere', ShapeStyle: 'Surface', ShapePartial: 0.55, Speed: [60, 85], Drag: 9,
          Orientation: 'VelocityParallel', Lifetime: [0.32, 0.48],
          Size: [[0, 4], [0.2, 13, 2.5], [1, 0]], Transparency: 0,
          LightEmission: 0.25, Brightness: 1.4, ZOffset: 0.5,
        },
      },
      {
        name: 'Shockwave', role: 'Shockwave', ref: 'Flat ground ring expanding on impact',
        position: [0, 0.25, 0], emits: [[0.3, 1]],
        props: {
          Texture: 'ring', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [0.32, 0.32], Size: [[0, 6], [0.35, 36], [1, 46]], Transparency: [[0, 0], [0.3, 0.1], [1, 1]],
          Color: '#ffe6a8', LightEmission: 0.4, Brightness: 1.3,
        },
      },
      {
        name: 'BlastRing', role: 'Shockwave', ref: 'Fast air ring at blast height',
        position: [0, C, 0], emits: [[0.3, 1]],
        props: {
          Texture: 'ring', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [0.22, 0.22], Size: [[0, 8], [1, 44]], Transparency: [[0, 0], [0.5, 0.3], [1, 1]],
          Color: '#ffffff', LightEmission: 1, Brightness: 1.6, ZOffset: 1,
        },
      },

      // ---------- 3. Aftermath ----------
      {
        name: 'Embers', role: 'Aftermath', ref: 'Sparks arcing out under gravity',
        position: [0, C, 0], part: { Size: [4, 4, 4] }, emits: [[0.3, 60]],
        props: {
          Texture: 'spark', Shape: 'Sphere', Speed: [28, 70], Drag: 2.2, Acceleration: [0, -38, 0],
          Lifetime: [0.6, 1.4], Orientation: 'VelocityParallel',
          Size: [[0, 1.6, 0.4], [1, 0.3]], Transparency: [[0, 0], [0.8, 0], [1, 1]],
          Color: [[0, '#fff3b0'], [0.4, '#ffb030'], [1, '#ff4010']], LightEmission: 1, Brightness: 3,
        },
      },
      {
        name: 'Debris', role: 'Aftermath', ref: 'Ground chunks kicked up from the crater',
        position: [0, 0.4, 0], part: { Size: [4, 0.2, 4] }, emits: [[0.32, 18]],
        props: {
          Texture: 'rock', Shape: 'Disc', EmissionDirection: 'Top', SpreadAngle: [50, 50],
          Speed: [30, 46], Acceleration: [0, -95, 0], Lifetime: [0.72, 0.82],
          Rotation: [0, 360], RotSpeed: [-500, 500], Size: [[0, 1.3, 0.5], [1, 1.1, 0.4]],
          Transparency: [[0, 0], [0.9, 0], [1, 1]], LightInfluence: 1, Brightness: 1.3,
        },
      },
      {
        name: 'Scorch', role: 'Aftermath', ref: 'Burnt crater decal',
        position: [0, 0.1, 0], emits: [[0.32, 1]],
        props: {
          Texture: 'scorch', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [2.25, 2.25], Rotation: [0, 360], Size: [[0, 12], [0.05, 18], [1, 18]],
          Transparency: [[0, 0], [0.8, 0], [1, 1]], LightInfluence: 1,
        },
      },
      {
        name: 'CrackGlow', role: 'Aftermath', ref: 'Molten cracks cooling',
        position: [0, 0.14, 0], emits: [[0.32, 1]],
        props: {
          Texture: 'crack_glow', Orientation: 'VelocityPerpendicular', EmissionDirection: 'Top', Speed: [0.01, 0.01],
          Lifetime: [1.6, 1.6], Size: [[0, 12], [0.07, 18], [1, 18]],
          Transparency: [[0, 0], [0.5, 0.2], [1, 1]], Color: [[0, '#ffffff'], [1, '#ff6020']],
          LightEmission: 1, Brightness: 2.2,
        },
      },
      {
        name: 'Afterburn', role: 'Aftermath', ref: 'Small flames licking up from the crater',
        position: [0, 0.3, 0], part: { Size: [9, 0.2, 9] }, rate: [[0.42, 1.35, 34]],
        props: {
          Texture: 'flame_spike', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [12, 12],
          Shape: 'Disc', EmissionDirection: 'Top', Orientation: 'FacingCameraWorldUp',
          Speed: [5, 9], Acceleration: [0, 6, 0], Lifetime: [0.35, 0.55],
          Size: [[0, 0.5], [0.3, 3.6, 1], [1, 0]], LightEmission: 0.2, Brightness: 1.3,
        },
      },
      {
        name: 'SmokeCloud', role: 'Aftermath', ref: 'Cel smoke the fireball erodes into',
        position: [0, C + 1, 0], part: { Size: [8, 6, 8] }, emits: [[0.4, 22]],
        props: {
          Texture: 'smoke_puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot',
          Shape: 'Sphere', ShapePartial: 0.7, Speed: [8, 15], Drag: 1.4, Acceleration: [0, 6, 0],
          Lifetime: [1.5, 2.1], Rotation: [0, 360], RotSpeed: [-25, 25],
          Size: [[0, 9], [0.3, 17, 3], [1, 20, 3]], Transparency: [[0, 0], [0.7, 0], [1, 1]],
          Color: [[0, '#ffb070'], [0.15, '#a8685a'], [0.4, '#625470'], [1, '#4e4760']],
          LightEmission: 0, LightInfluence: 0, ZOffset: -2.5,
        },
      },
      {
        name: 'GroundDust', role: 'Aftermath', ref: 'Low dust skirt pushed out by the shockwave',
        position: [0, 1, 0], part: { Size: [5, 1, 5] }, emits: [[0.32, 18]],
        props: {
          Texture: 'smoke_puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot',
          Shape: 'Cylinder', ShapeStyle: 'Surface', Speed: [26, 38], Drag: 4, Acceleration: [0, 2, 0],
          Lifetime: [0.9, 1.3], Rotation: [0, 360], Size: [[0, 4], [0.3, 9, 1.5], [1, 11, 2]], Transparency: [[0, 0], [0.7, 0], [1, 1]],
          Color: [[0, '#e0a080'], [1, '#6e6474']], LightEmission: 0, ZOffset: -1,
        },
      },
    ],
  };
})(typeof window !== 'undefined' ? window : globalThis);
