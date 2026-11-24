// SwordSlash v1 (steel) and FireSlash v1. A crescent hero drawn as 16 white layer flipbooks that
// appears at full length on drawing 1 (smear), holds 2 drawings, then thins from the inside,
// splits into streaks, dashes and needle shards. Life: tip glint, twinkles along the edge, sparks.
// Fire version: tongues trail backward off the cutting edge and boil; it burns out into wisps.
// The slash lies on a plane: EmissionDirection Top on a rotated part + Orientation VelocityPerpendicular.
(function (G) {
  const { stack, steps, flicker } = G.VFXSpec;
  G.VFX_EFFECTS = G.VFX_EFFECTS || {};

  const PLANE = { position: [1.2, 4.6, -4.6], rotation: [-57, 0, -33] }; // slash plane in front of the dummy
  const STAGE = (sword) => ({
    camera: [8.5, 5.8, -12.5], target: [0.3, 4.2, -3.6],
    dummy: { pos: [0, 0, 0], face: [0, 0, -10], sword },
    // right-arm swing (degrees about the swing axis): wind-up, cut, follow-through, recover
    swing: [[0, 115], [0.05, 120], [0.1, 35], [0.15, -45], [0.45, -52], [0.9, -12]],
  });

  function slash(o) {
    const fire = o.fire;
    const layers = [
      {
        name: 'TipGlint', role: 'Anticipation', ref: 'Glint on the blade tip a beat before the cut',
        position: [1.8, 8.4, -1.2], emits: [[0, 1]],
        props: {
          Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Speed: [0, 0], Lifetime: [0.14, 0.14],
          Rotation: [0, 0], Size: [[0, 2], [0.3, 5], [1, 3]], Color: o.glint, LightEmission: 1, Brightness: 3, ZOffset: 2,
        },
      },
      ...stack({
        name: 'Slash', role: 'Slash (hero)', ref: fire ? 'Fire crescent: tongues trail back, boil, burn out into wisps' : 'Crescent: smear, hold, thin from inside, streaks, dashes, shards',
        position: PLANE.position, rotation: PLANE.rotation, emits: [[0.09, 1]],
        props: {
          Texture: o.tex, FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Orientation: 'VelocityPerpendicular',
          EmissionDirection: 'Top', Speed: [0.01, 0.01], Lifetime: [o.life, o.life], Rotation: [o.rot, o.rot], Size: o.size,
        },
      }, o.colors),
      {
        name: 'EdgeTwinkles', role: 'Life', ref: 'Glints popping along the edge while it holds',
        position: PLANE.position, rotation: PLANE.rotation, part: { Size: [o.size * 0.7, 0.3, o.size * 0.7] }, rate: [[0.1, 0.42, 34]],
        props: {
          Texture: 'glint', FlipbookLayout: 'Grid2x2', FlipbookMode: 'OneShot', Shape: 'Box', Speed: [0, 0],
          Lifetime: [0.12, 0.18], Rotation: [0, 0], Size: [[0, 1.6, 0.8], [1, 1.6, 0.8]], Color: o.glint, LightEmission: 1, Brightness: 2.5, ZOffset: 1.5,
        },
      },
      {
        name: 'Sparks', role: 'Life', ref: 'Needle sparks thrown off the cut',
        position: PLANE.position, rotation: PLANE.rotation, part: { Size: [o.size * 0.75, 0.3, o.size * 0.75] }, emits: [[0.1, 16]], rate: [[0.12, 0.4, 20]],
        props: {
          Texture: 'spark', Shape: 'Disc', ShapeStyle: 'Surface', EmissionDirection: 'Top', SpreadAngle: [80, 80],
          Speed: [18, 42], Drag: 3.5, Acceleration: [0, fire ? 4 : -25, 0], Lifetime: [0.18, 0.42], Orientation: 'VelocityParallel',
          Size: [[0, 1.1, 0.3], [1, 0.2]], Color: o.spark, LightEmission: 1, Brightness: 3,
        },
      },
    ];
    if (fire) {
      layers.push({
        name: 'Wisps', role: 'Life', ref: 'Flame tongues peeling off the slash and rising (boil at 12 fps)',
        position: PLANE.position, rotation: PLANE.rotation, part: { Size: [o.size * 0.7, 0.3, o.size * 0.7] }, emits: [[0.12, 6]], rate: [[0.14, 0.55, 20]],
        props: {
          Texture: 'flame_lick', FlipbookLayout: 'Grid2x2', FlipbookMode: 'Random', FlipbookFramerate: [12, 12], Shape: 'Box',
          Speed: [0.5, 1], Acceleration: [0, 22, 0], Orientation: 'VelocityParallel', Lifetime: [0.3, 0.5],
          Size: [[0, 0.8], [0.3, 2.4, 0.6], [1, 0]], Color: [[0, '#ffe080'], [0.3, '#ff8a1a'], [1, '#c8280a']], LightEmission: 0.3, Brightness: 1.4, ZOffset: 0.4,
        },
      }, {
        name: 'HeatSmoke', role: 'Life', ref: 'Small dark puffs where the flames burn out',
        position: [0.4, 5, -3.6], part: { Size: [9, 3, 2] }, emits: [[0.38, 6]],
        props: {
          Texture: 'puff', FlipbookLayout: 'Grid4x4', FlipbookMode: 'OneShot', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [25, 25],
          Speed: [3, 6], Acceleration: [0, 3, 0], Lifetime: [0.8, 1.1], Rotation: [-15, 15], Size: [[0, 2], [0.4, 4, 0.8], [1, 5, 1]],
          Color: [[0, '#6a3a34'], [1, '#3a3442']], ZOffset: -1,
        },
      }, {
        name: 'Embers', role: 'Life', ref: 'Embers drifting up after the cut',
        position: [0.4, 4, -3.6], part: { Size: [10, 6, 2] }, rate: [[0.2, 0.85, 22]],
        props: {
          Texture: 'spark', Shape: 'Box', EmissionDirection: 'Top', SpreadAngle: [35, 35], Speed: [3, 8], Acceleration: [0, 6, 0],
          Lifetime: [0.4, 0.8], Orientation: 'VelocityParallel', Size: [[0, 0.6, 0.2], [1, 0.1]],
          Color: [[0, '#ffe080'], [1, '#ff4a10']], LightEmission: 1, Brightness: 3,
        },
      });
    }
    return layers;
  }

  G.VFX_EFFECTS.SwordSlash = {
    name: 'SwordSlash', version: 1, duration: 1.05,
    stage: STAGE('steel'),
    beats: [[0, 'Tip glint (anticipation)'], [0.09, 'Smear drawing'], [0.13, 'Full slash holds 2 drawings'], [0.3, 'Thins from inside, splits into streaks'], [0.5, 'Dashes and shards drift off']],
    lights: [{ name: 'SlashLight', position: [0.4, 4.5, -3.6], Color: '#8fd0ff', Range: 22, Brightness: [[0, 0], [0.09, 0], [0.11, 2.4], [0.3, 1], [0.7, 0]] }],
    impactFrames: [{ t: 0.1, dur: 0.034, Brightness: 0.15, Contrast: 0.3, Saturation: -0.2, TintColor: '#e0f0ff' }],
    shakes: [{ t: 0.1, dur: 0.22, amp: 0.22, freq: 30 }],
    layers: slash({
      tex: 'fx_slash', size: 13, life: 0.62, rot: 180,
      glint: '#e8f6ff', spark: [[0, '#ffffff'], [1, '#6cc8ff']],
      colors: {
        glow: { Color: '#2f9cff', Transparency: steps([0.5, 0.36, 0.52, 0.4, 0.62, 0.8, 0.94, 1], 1) },
        rim: { Color: '#0b2470' },
        mid: { Color: [[0, '#b8f0ff'], [0.4, '#7fd2ff'], [1, '#4a9cff']] },
        core: { Color: '#ffffff', Brightness: 2.2, Transparency: steps(flicker(0.03, 0.06, 8, 11)) },
      },
    }),
  };

  G.VFX_EFFECTS.FireSlash = {
    name: 'FireSlash', version: 1, duration: 1.7,
    stage: STAGE('fire'),
    beats: [[0, 'Tip glint (anticipation)'], [0.09, 'Smear drawing'], [0.13, 'Flaming crescent holds, tongues boil'], [0.4, 'Tongues pinch off into wisps'], [0.6, 'Burns out: embers, heat smoke']],
    lights: [{ name: 'FireLight', position: [0.4, 4.5, -3.6], Color: '#ff8a30', Range: 26, Brightness: [[0, 0], [0.09, 0], [0.11, 3.2], [0.2, 2], [0.26, 2.6], [0.34, 1.7], [0.42, 2.1], [0.9, 0]] }],
    impactFrames: [{ t: 0.1, dur: 0.034, Brightness: 0.3, Contrast: 0.3, Saturation: -0.1, TintColor: '#fff0d8' }],
    shakes: [{ t: 0.1, dur: 0.28, amp: 0.3, freq: 28 }],
    layers: slash({
      fire: true, tex: 'fx_fireslash', size: 17, life: 0.8, rot: 180,
      glint: '#fff0c0', spark: [[0, '#fff3b0'], [0.5, '#ffa020'], [1, '#ff4010']],
      colors: {
        glow: { Color: '#ff5a14', Transparency: steps([0.6, 0.5, 0.64, 0.52, 0.66, 0.78, 0.9, 0.97, 1], 1) },
        rim: { Color: '#5e0804' },
        mid: { Color: [[0, '#ffa424'], [0.5, '#ff7616'], [1, '#d8400c']] },
        core: { Color: [[0, '#ffffff'], [0.5, '#fff0b0'], [1, '#ffcc50']], Brightness: 1.9, Transparency: steps(flicker(0.04, 0.08, 9, 13)) },
      },
    }),
  };
})(typeof window !== 'undefined' ? window : globalThis);
