# Effect spec (JSON) reference

Units are studs, times seconds from the cast. Origin = caster's feet, facing -Z, Y up.
Keys: a value is either constant or a key list `[[k, value, ease?], ...]`. For shells and beams `k` is 0..1 of
the item's life; for `pose`, `lights.brightness` and `camera` it is seconds/normalised as noted. Eases: `in`,
`out`, `outExpo`, `outBack`, linear by default.

```jsonc
{
  "name": "000_FireFist", "title": "Fire Fist", "element": "Flame", "archetype": "projectile",
  "duration": 2.2,
  "layers": [ /* emitter | shell | beam | bolt | trail | vbeam | rig */ ],
  "hitstop": [{"t": 0.74, "dur": 0.08}],          // rule 4
  "hits":    [{"t": 0.74, "dummy": 0, "dir": [0,0,-1], "power": 1.0}],
  "numbers": [{"t": 0.74, "at": [0,6.2,-24], "text": "115", "color": "#ffb02a", "vel": [3,17,0], "size": 2.6}],
  "ghosts":  [{"t": 0.25, "at": [0,0,-5], "color": "#ff5a14", "life": 0.4}],   // dash afterimages
  "debris":  [{"kind": "crater"|"fling", "at": [..], "t": .., "radius": 8, "count": 14, "size": 3, "speed": 30, "life": 3}],
  "lights":  [{"at": [..], "color": "#..", "range": 22, "brightness": [[t, v], ...], "move": {..}}],
  "shakes":  [{"t": .., "amp": 0.6, "dur": 0.4, "freq": 22}],
  "impact":  [{"t": .., "dur": 0.05, "mode": "invert"|"mono"|"white"|"black"}],
  "grade":   [[t, brightness, contrast, saturation, "#tint"], ...],          // ColorCorrection keys
  "pose":    {"lean": [[t, deg]], "twist": .., "armR": .., "armL": .., "armRz": .., "armLz": .., "offset": [[t,[x,y,z]]], "scale": [[t,[x,y,z]]]},
  "camera":  {"pos": .., "look": .., "fov": ..}, "poster": 0.8, "dummies": [[0,0,-24]]   // previewer only
}
```

## Layers
- **emitter** (ParticleEmitter): `at`, `rot` (deg, CFrame.Angles order), `props` (Roblox property names; sequences
  as `[[t, v, envelope]]`, ranges as `[min, max]`, colours as hex or `[[t, hex]]`, enums as names), `emits`
  `[[t, count]]` and/or `rate` `[[t0, t1, perSecond]]`, optional `move` `{from, to, t0, t1, ease, arc}`,
  `part` `[sx, sy, sz]` for shape emission, `seed` (stacks share one), `stack` (texture family).
- **shell** (Part + SpecialMesh FileMesh): `mesh`, `material` Neon|ForceField|Glass|Ice|Textured, `texture`,
  `t0`, `life`, `scale` keys (number or [x,y,z]), `transparency` keys, `color` (hex or keys), `rot`, `spin`
  (deg/s or keys) + `spinAxis`, `move`, `velocity`, `scroll`, `tile`, `brightness`.
- **beam**: `from`, `to` (both may be keys over life), `t0`, `life`, `texture` or `textures` + `swap`, `color`,
  `width` keys ([w0, w1]), `reach` keys (0..1 of the length drawn), `curve` (studs the middle bows out, keys allowed;
  Roblox: attachment Axis + CurveSize0/1 = |c| * 4/3 so the Bezier midpoint matches), `lightEmission`,
  `textureSpeed` (texture lengths/s), `textureLength`, `transparency`, `segments`.
- **bolt** (neon zig-zag parts): `from`, `to`, `t0`, `life`, `color`, `thickness`, `jitter`, `segments`,
  `flicker` (rebuild interval), `seed`.
- **trail** (Roblox `Trail` on two attachments): rides `path` / `move` / `wave` (below); emits while
  `t0 <= t <= t1`. `lifetime` (s), `width` (studs between the attachments, laid along `up`, default `[0,1,0]`
  in the cast frame), `faceCamera` (width turns toward the camera instead), `widthScale`, `transparency`
  (number sequences over a point's age, as emitter props), `color` (hex or colour sequence over age),
  `texture` or `textures` + `swap` (cycle strip variants every `swap` s), `textureMode` Stretch | Wrap | Static,
  `textureLength`, `lightEmission` (0 = alpha blend for dark anchors, 1 = additive), `brightness`.
  Trail points age on **real** time, as in Roblox: during a hit-stop the head holds, the tail keeps fading.
  Stack textures as separate trails (glow / mid / core, plus a dark alpha-blended under-ribbon).
- **vbeam** (volumetric beam): `from`, `to` (keys over life allowed), `t0`, `life`, `reach` keys.
  `core` and optional `sheath`: cylinder Parts `{radius, color, transparency, material Neon|ForceField}` (keys
  over life). `planes`: one set or a list of sets of crossed Beams (FaceCamera off) fanned evenly over 180
  degrees around the axis: `{count, width [w0, w1] keys (taper), texture | textures + swap, color,
  transparency, textureLength, textureSpeed, twist (deg/s), angle (deg offset), lightEmission, brightness}`.
  Typical stack: a navy alpha-blended set (dark anchor), a blue glow set, a white-hot core set twisting the
  other way. Keep the Neon core thin (radius <= 0.2) and the sheath dim: both bloom white on sand.

- **rig** (skinned model following a path): `model` (previewer `assets/models/<model>.glb`, Roblox a skinned
  MeshPart named `<model>` in `AnimeVFX.Models`), `t0`, `life`, `path` / `move` / `wave` for the head,
  `bones.prefix` (default `spine_`, `00` = head .. tail), `jawBone` + `jaw` keys (deg, over life), `roll` keys,
  `transparency` keys, `color` / `brightness` (previewer tint). Each spine bone sits a fixed arc length behind the
  head along the head's past trajectory, so the body traces the path (S-curves, real coils); before the head has
  travelled a body length, the unborn part continues straight back from the start point (hide it behind a
  portal effect or the caster; the creature pours out of it without folding). Models are
  built straight along -Z (head at -Z); see `scripts/rig_serpent.py`.

## Paths (any layer with an attachment: emitter, shell, trail, light)
- `path`: `[[t, [x,y,z], ease?], ...]` polyline keyed on absolute effect time (zig-zag dashes, multi-leg routes).
- `move`: `{from, to, t0, t1, ease, arc}` one eased leg with a vertical arc.
- `wave`: `{amp, freq, axis, phase, t0}` added on top: `axis * amp * sin(2*pi*freq*(t - t0) + phase deg)`;
  `amp` may be keys on absolute time (S-curves that swell, tighten or die out). Give braided ribbons the same
  path and different `phase`.
