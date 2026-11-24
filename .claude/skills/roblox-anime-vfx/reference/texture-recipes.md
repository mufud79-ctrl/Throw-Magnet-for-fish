# Texture recipes (vfx/engine/textures.js)

All textures are drawn procedurally so the preview and the uploaded PNG are identical.
Register new ones in `DEFS` with `{ build, grid: [cols, rows], note }`. The build script finds
names with the regex `^    name: { build:`, so keep that indentation.

## Building blocks

- `flip(size, cols, rows, fn(u, v, frame01, index, out))` is a per-pixel flipbook, `pix(size, fn)`
  a single frame. `u, v` are 0–1 inside the cell, with v pointing down. Write RGBA 0–1 into `out`.
- `aa(x, edge, w)` is an anti-aliased hard step. Every cel edge goes through it. A smaller `w`
  gives a crisper edge, but don't go below ~1px of field change.
- `bands(h, [[thr, rgb], ...])` is a stepped color ramp over a scalar field ("heat", "shade").
- `fbm(noise, x, y, octaves)` is seeded value noise. Each generator uses fixed seeds, so the
  output is deterministic.
- Canvas 2D helpers for line work: `strokePaths`, `jagged` (scorch/cracks), polygons (rock).

## Patterns

| Want | Recipe |
|---|---|
| Fire/smoke puff that dissipates | field = blob + fbm; `vis = min(base, (cut - (f*1.05 - 0.12)) * 4)` eats holes as frame f rises; ink rim = `mix(INK, c, aa(vis, 0.1, w))` |
| Tongue / spike | width profile `w(y)` sharp at tip, rounded at base, S-curve offset; 2×2 variants for Random boil |
| Cel-lit volume | fake sphere normals from blob distance, `dot(n, L)`, 3 bands, greyscale; tint via ColorSequence |
| Glow orb | concentric hard rings with decreasing alpha (no gaussian) |
| Streak | diamond field `1 - (|x|/w + |y|)`, fatter toward the head (+Y = velocity) |
| Ring | thin crisp outer band + faint broken trailing band (otherwise it reads as a plate) |

## Review

`node headless.mjs <Name> textures` writes `out/<Name>/texture_sheet.png` (all frames on a
dark ground). Check that flipbook frame 0 fills ~80% of the cell, edges are crisp, and the last
frames are nearly empty.
