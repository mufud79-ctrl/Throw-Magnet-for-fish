# Effect spec (JSON) reference

Units are studs, times seconds from the cast. Origin = caster's feet, facing -Z, Y up.
Keys: a value is either constant or a key list `[[k, value, ease?], ...]`. For shells and beams `k` is 0..1 of
the item's life; for `pose`, `lights.brightness` and `camera` it is seconds/normalised as noted. Eases: `in`,
`out`, `outExpo`, `outBack`, linear by default.

```jsonc
{
  "name": "000_FireFist", "title": "Fire Fist", "element": "Flame", "archetype": "projectile",
  "duration": 2.2,
  "layers": [ /* emitter | shell | beam | bolt */ ],
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
- **beam**: `from`, `to`, `t0`, `life`, `texture`, `color`, `width` keys ([w0, w1]), `reach` keys (0..1 of the
  length drawn), `lightEmission`, `textureSpeed` (texture lengths/s), `textureLength`, `transparency`.
- **bolt** (neon zig-zag parts): `from`, `to`, `t0`, `life`, `color`, `thickness`, `jitter`, `segments`,
  `flicker` (rebuild interval), `seed`.
