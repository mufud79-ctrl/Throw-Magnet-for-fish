// Checks a spec against Roblox's ParticleEmitter rules so the exported Luau won't error in Studio.
const PROPS = new Set(['Brightness', 'Color', 'LightEmission', 'LightInfluence', 'Orientation', 'Size', 'Squash', 'Texture',
  'Transparency', 'ZOffset', 'EmissionDirection', 'Lifetime', 'Rate', 'Rotation', 'RotSpeed', 'Speed', 'SpreadAngle', 'Shape',
  'ShapeInOut', 'ShapeStyle', 'ShapePartial', 'Acceleration', 'Drag', 'LockedToPart', 'TimeScale', 'VelocityInheritance',
  'WindAffectsDrag', 'Enabled', 'FlipbookLayout', 'FlipbookMode', 'FlipbookFramerate', 'FlipbookStartRandom']);
const ENUM = {
  Orientation: ['FacingCamera', 'FacingCameraWorldUp', 'VelocityParallel', 'VelocityPerpendicular'],
  EmissionDirection: ['Top', 'Bottom', 'Front', 'Back', 'Left', 'Right'],
  Shape: ['Box', 'Sphere', 'Cylinder', 'Disc'], ShapeStyle: ['Volume', 'Surface'], ShapeInOut: ['Outward', 'Inward', 'InAndOut'],
  FlipbookLayout: ['None', 'Grid2x2', 'Grid4x4', 'Grid8x8'], FlipbookMode: ['Loop', 'OneShot', 'PingPong', 'Random'],
};
export function lint(fx, textureNames) {
  const errs = [], warn = [];
  const seq = (where, v, isColor) => {
    if (typeof v !== 'object') return;
    if (v.length < 2 || v.length > 20) errs.push(`${where}: needs 2-20 keypoints`);
    if (v[0][0] !== 0 || v[v.length - 1][0] !== 1) errs.push(`${where}: first keypoint must be t=0 and last t=1`);
    for (let i = 1; i < v.length; i++) if (v[i][0] <= v[i - 1][0]) errs.push(`${where}: keypoint times must increase`);
    if (!isColor) for (const k of v) if ((k[2] || 0) < 0) errs.push(`${where}: negative envelope`);
  };
  for (const L of fx.layers) {
    if (L.mesh) { if (!L.texture) errs.push(`${L.name}: mesh without texture`); if (!(L.life > 0)) errs.push(`${L.name}: mesh needs life`); continue; }
    const p = L.props, w = `${L.name}`;
    for (const k of Object.keys(p)) if (!PROPS.has(k)) errs.push(`${w}: unknown ParticleEmitter property ${k}`);
    for (const [k, vals] of Object.entries(ENUM)) if (p[k] !== undefined && !vals.includes(p[k])) errs.push(`${w}: ${k}=${p[k]} is not a valid enum`);
    if (!p.Texture) errs.push(`${w}: no Texture`);
    else if (textureNames && !textureNames.includes(p.Texture)) errs.push(`${w}: texture ${p.Texture} is not generated`);
    ['Size', 'Transparency', 'Squash'].forEach((k) => seq(`${w}.${k}`, p[k]));
    seq(`${w}.Color`, p.Color, true);
    if (p.Lifetime && Math.max(...[].concat(p.Lifetime)) > 20) errs.push(`${w}: Lifetime max is 20`);
    if (p.ShapePartial !== undefined && (p.ShapePartial < 0 || p.ShapePartial > 1)) errs.push(`${w}: ShapePartial must be 0-1`);
    if (p.LightEmission !== undefined && (p.LightEmission < 0 || p.LightEmission > 1)) errs.push(`${w}: LightEmission must be 0-1`);
    if (p.Squash && typeof p.Squash === 'object' && p.Squash.some((k) => Math.abs(k[1]) > 3)) errs.push(`${w}: Squash range is -3..3`);
    if (p.Shape && p.Shape !== 'Box' && !L.part) warn.push(`${w}: Shape ${p.Shape} without part.Size emits from a point`);
    if (!L.emits && !L.rate) warn.push(`${w}: never emits`);
    const end = Math.max(0, ...(L.emits || []).map((e) => e[0]), ...(L.rate || []).map((r) => r[1])) + Math.max(...[].concat(p.Lifetime || 1));
    if (end > fx.duration + 0.3) warn.push(`${w}: particles outlive duration (${end.toFixed(2)}s > ${fx.duration}s), cleanup will cut them`);
    if ((L.emits || []).reduce((s, e) => s + e[1], 0) > 200) warn.push(`${w}: >200 particles in one layer, check mobile perf`);
  }
  // stacked heroes: every layer must move identically or they drift apart in Roblox
  const stacks = {};
  for (const L of fx.layers) if (L.stack) (stacks[L.stack] = stacks[L.stack] || []).push(L);
  const SHARED = ['Lifetime', 'Speed', 'Rotation', 'RotSpeed', 'SpreadAngle', 'Acceleration', 'Drag', 'Size', 'Squash', 'Orientation', 'EmissionDirection', 'Shape', 'FlipbookLayout', 'FlipbookMode'];
  for (const [name, Ls] of Object.entries(stacks)) {
    const a = Ls[0];
    for (const L of Ls) {
      for (const k of ['position', 'rotation', 'part', 'emits', 'rate']) if (JSON.stringify(L[k]) !== JSON.stringify(a[k])) errs.push(`${L.name}: ${k} differs from ${a.name} (stack ${name})`);
      for (const k of SHARED) if (JSON.stringify(L.props[k]) !== JSON.stringify(a.props[k])) errs.push(`${L.name}: ${k} differs within stack ${name}`);
      const p = L.props;
      for (const k of ['Lifetime', 'Speed', 'Rotation', 'RotSpeed']) if (Array.isArray(p[k]) && p[k][0] !== p[k][1]) errs.push(`${L.name}: ${k} must be fixed (min = max) in a stack`);
      for (const k of ['Size', 'Squash']) if (Array.isArray(p[k]) && p[k].some((kp) => kp[2])) errs.push(`${L.name}: ${k} envelope breaks stack alignment`);
      if (p.SpreadAngle && (p.SpreadAngle[0] || p.SpreadAngle[1])) errs.push(`${L.name}: SpreadAngle must be 0 in a stack`);
      if (L.part) errs.push(`${L.name}: stacked layers must be point emitters (no part.Size)`);
    }
  }
  return { errs, warn };
}
