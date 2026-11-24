// CeroBeam: Bleach's Cero. Spiritual pressure gathers into a churning sphere at the palm, then fires
// as a massive straight beam that "churns and rotates like a spinning blade" (Gran Rey Cero).
// Built the same way as the references: ForceField meshes for the beam body, particles for life.
(function (G) {
  const { stack, part, compose, faceRot } = G.VFXSpec;
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};
  const mesh = (name, ref, o) => Object.assign({ name, ref }, o, { props: { Texture: o.texture } });
  const HAND = [2.4, 4.3, 0];
  const LEN = 60, MID = [HAND[0] + LEN / 2, HAND[1], 0], END = [HAND[0] + LEN, HAND[1], 0];
  const ALONG = [0, 0, -90];                               // rotates local +Y (mesh axis) onto +X (beam direction)
  const STAGE = { env: 'stone', bloom: [0.45, 1.0], camera: [-5, 6, 17], target: [14, 4, 0], dummy: { pos: [0, 0, 0], face: [10, 0, 0], color: '#2a2630' } };
  const REDGRADE = [[0, 0, 0, 0, '#ffffff'], [0.6, -0.05, 0.2, 0.05, '#ffe2e2'], [0.75, -0.04, 0.25, 0.1, '#ffd4d4'], [2.1, -0.04, 0.25, 0.1, '#ffd4d4'], [2.6, 0, 0, 0, '#ffffff']];

  part({
    name: 'CeroCharge', duration: 0.78, stage: STAGE, grade: REDGRADE, previewAt: [0, 0, 0],
    note: 'Reiatsu gathers into a churning red sphere at the palm',
    lights: [{ name: 'Charge', position: HAND, Color: '#ff3048', Range: 18, Brightness: [[0, 0], [0.7, 2], [0.78, 3]] }],
    layers: [
      mesh('Ball', 'Churning ForceField sphere', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#ff2a40', brightness: 1.7, position: HAND, rotation: [30, 0, 20], spin: 800, spawns: [0], life: 0.78, size: [[0, 0.3], [0.85, 2.8, 'out'], [1, 3.4]], scroll: [1.2, 0] }),
      mesh('Core', 'White-hot core', { mesh: 'sphere', texture: 'm_solid', material: 'Neon', color: '#fff0f0', brightness: 1.5, position: HAND, spawns: [0], life: 0.78, size: [[0, 0.15], [0.85, 1.5], [1, 1.9]] }),
      ...[0, 1, 2].map((k) => mesh(`Halo${k + 1}`, 'Slash band whipping around the ball', { mesh: 'band', meshArgs: { arc: 300, inner: 0.72, cone: 0.1 }, texture: 'm_slash', material: 'ForceField', color: '#ff6070', brightness: 2, fresnel: 0.3, position: HAND, rotation: [[60, 0, 0], [0, 0, 70], [40, 50, -30]][k], spin: (k % 2 ? -1 : 1) * 1500, spawns: [0.15 + k * 0.12, 0.45 + k * 0.08], life: 0.24, size: [[0, 2.5], [1, 4.5]], transparency: [[0, 0], [0.6, 0.1], [1, 1]] })),
      { name: 'Gather', ref: 'Red lines sucked into the palm', position: HAND, part: { Size: [14, 14, 14] }, rate: [[0, 0.7, 90]],
        props: { Texture: 'line', Shape: 'Sphere', ShapeStyle: 'Surface', ShapeInOut: 'Inward', Speed: [30, 40], Lifetime: [0.2, 0.22], Orientation: 'VelocityParallel', Size: [[0, 0], [0.3, 4, 1], [1, 1]], Color: [[0, '#ff4058'], [1, '#ffe0e4']], LightEmission: 1, Brightness: 2.2 } },
      { name: 'Motes', ref: 'Reiatsu motes drifting in', position: HAND, part: { Size: [8, 8, 8] }, rate: [[0, 0.7, 40]],
        props: { Texture: 'sparkle', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [16, 22], Shape: 'Sphere', ShapeInOut: 'Inward', Speed: [6, 10], Lifetime: [0.35, 0.45], Size: [[0, 0.5, 0.2], [1, 0.2]], Color: '#ffb0bc', LightEmission: 1, Brightness: 2.4 } },
    ],
  });

  part({
    name: 'CeroBeamFire', duration: 1.6, stage: STAGE, grade: REDGRADE, previewAt: [0, 0, 0],
    note: 'Massive red beam: nested ForceField cylinders churning like a blade, spirals, travelling shock rings, impact blast',
    impactFrames: [
      { t: 0, dur: 0.034, Brightness: 0.6, Contrast: 0.2, Saturation: -0.2 },
      { t: 0.034, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, Void: '#000000', Highlight: { FillColor: '#ffffff' } },
      { t: 0.084, dur: 0.05, Brightness: -0.15, Contrast: 9, Saturation: -1, TintColor: '#ff2030', Void: '#000000', Highlight: { FillColor: '#000000' } },
    ],
    shakes: [{ t: 0, dur: 1.1, amp: 1.1, freq: 26 }],
    lights: [{ name: 'Muzzle', position: HAND, Color: '#ff3048', Range: 26, Brightness: [[0, 3.5], [0.2, 2.2], [1.0, 1.5], [1.3, 0]] }, { name: 'Impact', position: END, Color: '#ff5060', Range: 34, Brightness: [[0, 0], [0.05, 4], [0.4, 2.5], [1.3, 0]] }],
    layers: [
      // ---- beam body (mesh axis Y rotated onto +X; Size Y = length) ----
      mesh('Outer', 'Crimson outer sheath, streaks flowing forward, churning', { mesh: 'cylinder', texture: 'm_beam', material: 'ForceField', color: '#e00828', brightness: 0.95, fresnel: 2.6, position: MID, rotation: ALONG, spin: 520, spawns: [0], life: 1.15, size: [[0, [1, LEN, 1]], [0.05, [10, LEN, 10], 'out'], [0.7, [9, LEN, 9]], [1, [0.6, LEN, 0.6], 'in']], transparency: [[0, 0], [0.8, 0.1], [1, 1]], scroll: [0.2, -4.5] }),
      mesh('Mid', 'Pink-red mid layer, counter-rotating', { mesh: 'cylinder', texture: 'm_beam', material: 'ForceField', color: '#ff2a48', brightness: 0.35, fresnel: 1.0, position: MID, rotation: ALONG, spin: -700, spawns: [0], life: 1.12, size: [[0, [0.6, LEN, 0.6]], [0.05, [5.4, LEN, 5.4], 'out'], [0.7, [4.8, LEN, 4.8]], [1, [0.3, LEN, 0.3], 'in']], scroll: [-0.4, -7] }),
      mesh('Core', 'White-hot core', { mesh: 'cylinder', texture: 'm_solid', material: 'Neon', color: '#fff2f4', brightness: 1.1, position: MID, rotation: ALONG, spawns: [0], life: 1.1, size: [[0, [0.3, LEN, 0.3]], [0.05, [1.5, LEN, 1.5], 'out'], [0.75, [1.2, LEN, 1.2]], [1, [0.1, LEN, 0.1], 'in']] }),
      mesh('Spiral', 'Bright spiral ribbon wound around the beam', { mesh: 'spiral', meshArgs: { turns: 8, width: 0.04 }, texture: 'm_spiral', material: 'ForceField', color: '#ff3048', brightness: 0.8, fresnel: 0.3, position: MID, rotation: ALONG, spin: -900, spawns: [0.03], life: 1.0, size: [[0, [3, LEN, 3]], [0.08, [10.5, LEN, 10.5], 'out'], [1, [9, LEN, 9]]], transparency: [[0, 0], [0.7, 0.15], [1, 1]] }),
      mesh('InkSpiral', 'Dark crimson ink spiral for contrast', { mesh: 'spiral', meshArgs: { turns: 6, width: 0.05 }, texture: 'm_spiral', material: 'Ink', color: '#1a0008', position: MID, rotation: ALONG, spin: 1000, spawns: [0.05], life: 0.95, size: [[0, [3, LEN, 3]], [0.08, [9.6, LEN, 9.6], 'out'], [1, [8.6, LEN, 8.6]]], transparency: [[0, 0], [0.7, 0.15], [1, 1]] }),
      mesh('Rings', 'Shock rings racing down the beam', { mesh: 'torus', meshArgs: { tube: 0.05 }, texture: 'm_solid', material: 'ForceField', color: '#ff6a80', brightness: 0.7, fresnel: 0.6, position: HAND, rotation: ALONG, velocity: [75, 0, 0], spawns: [0, 0.18, 0.36], life: 0.75, size: [[0, [6, 2, 6]], [1, [12, 2, 12]]], transparency: [[0, 0], [0.8, 0.4], [1, 1]] }),
      mesh('Crown', 'Slash crown spinning around the muzzle', { mesh: 'band', meshArgs: { arc: 360, inner: 0.6, cone: 0.25 }, texture: 'm_slash', material: 'ForceField', color: '#ff5060', brightness: 1.3, fresnel: 0.3, position: [HAND[0] + 0.6, HAND[1], 0], rotation: ALONG, spin: 1600, spawns: [0, 0.25, 0.5, 0.75], life: 0.26, size: [[0, 5], [1, 13]], transparency: [[0, 0], [0.5, 0.1], [1, 1]] }),
      mesh('Muzzle', 'Muzzle orb', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#ff3048', brightness: 1.0, position: HAND, spin: 900, spawns: [0], life: 1.1, size: [[0, 3], [0.05, 6, 'out'], [0.8, 5.2], [1, 0.5, 'in']], scroll: [1.5, 0] }),
      // ---- impact at the far end ----
      mesh('Blast', 'Impact sphere at the end of the beam', { mesh: 'sphere', texture: 'm_swirl', material: 'ForceField', color: '#ff3a50', brightness: 0.9, position: END, spin: 400, spawns: [0.08], life: 1.2, size: [[0, 4], [0.1, 15, 'out'], [0.7, 17], [1, 20]], transparency: [[0, 0], [0.7, 0.2], [1, 1]], scroll: [0.8, 0.2] }),
      ...stack({ name: 'BlastFlash', role: 'hero', ref: 'Radial red-white burst', position: END, emits: [[0.08, 1]],
        props: { Texture: 'fire_burst', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Orientation: 'FacingCamera', Speed: [0, 0], Lifetime: [0.6, 0.6], Rotation: [0, 0], Size: 30, ZOffset: 2 } },
      { glow: { Color: '#ff2040', Transparency: 0.6 }, rim: { Color: '#8a0614', LightEmission: 0.2 }, mid: { Color: '#e8304a', LightEmission: 0.4 }, core: { Color: '#fff0f2', LightEmission: 1, Brightness: 1.4 } }),
      { name: 'BlastShards', ref: 'Shards blown off the impact', position: END, part: { Size: [4, 4, 4] }, emits: [[0.08, 60]], rate: [[0.1, 1.0, 40]],
        props: { Texture: 'spark', Shape: 'Sphere', Speed: [30, 80], Drag: 3, Acceleration: [0, -20, 0], Lifetime: [0.3, 0.7], Orientation: 'VelocityParallel', Size: [[0, 2, 0.6], [1, 0.4]], Color: [[0, '#ffffff'], [0.4, '#ff8090'], [1, '#ff2030']], LightEmission: 1, Brightness: 3 } },
      { name: 'BlastSmoke', ref: 'Dark smoke boiling off the impact', position: [END[0], 2, 0], part: { Size: [8, 4, 8] }, emits: [[0.2, 10]], rate: [[0.3, 1.2, 10]],
        props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [50, 50], Speed: [4, 10], Lifetime: [0.8, 1.1], Rotation: [0, 360], Size: [[0, 8], [1, 16, 3]], Color: '#3a2228', LightEmission: 0, Transparency: [[0, 0.2], [1, 1]], ZOffset: -2 } },
      // ---- life along the beam ----
      { name: 'Streamers', ref: 'Sparks streaming along the beam', position: MID, part: { Size: [LEN, 7, 7] }, rate: [[0.03, 1.0, 70]],
        props: { Texture: 'spark', Shape: 'Box', EmissionDirection: 'Right', SpreadAngle: [6, 6], Speed: [50, 90], Lifetime: [0.15, 0.3], Orientation: 'VelocityParallel', Size: [[0, 2.2, 0.6], [1, 0.4]], Color: [[0, '#ffffff'], [1, '#ff5068']], LightEmission: 1, Brightness: 2.6 } },
      { name: 'GroundDust', ref: 'Dust torn up under the beam', position: [MID[0], 0.6, 0], part: { Size: [LEN, 0.4, 8] }, rate: [[0.05, 1.1, 40]],
        props: { Texture: 'dust', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [40, 40], Speed: [4, 9], Lifetime: [0.5, 0.8], Rotation: [0, 360], Size: [[0, 3], [1, 8, 1.5]], Color: '#6a3a40', LightEmission: 0.15, Transparency: [[0, 0.3], [1, 1]], ZOffset: -2 } },
      { name: 'MuzzleGlints', ref: 'Glints popping at the muzzle', position: HAND, part: { Size: [5, 5, 5] }, rate: [[0, 1.0, 18]],
        props: { Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [0, 0], Lifetime: [0.12, 0.18], Rotation: [0, 0], Size: [[0, 3, 1], [1, 3, 1]], Color: '#ffe8ec', LightEmission: 1, Brightness: 2.6, ZOffset: 3 } },
    ],
  });

  G.VFX_EFFECTS.CeroBeam = compose({ name: 'CeroBeam', version: 1, stage: STAGE, duration: 2.6, grade: REDGRADE, note: 'Bleach Cero: charge at the palm, then a churning red beam' }, [
    { part: 'CeroCharge', t: 0, label: '0.00 charge' },
    { part: 'CeroBeamFire', t: 0.75, label: '0.75 fire' },
  ]);
  void faceRot;
})(typeof window !== 'undefined' ? window : globalThis);
