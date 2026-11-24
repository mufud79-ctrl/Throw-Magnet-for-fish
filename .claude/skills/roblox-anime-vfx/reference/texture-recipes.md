# Drawing recipes (vfx/engine/paint.js)

Every texture is drawn procedurally as signed-distance shapes. That makes the preview and the
uploaded PNG identical, and lets one drawing split into 4 aligned white layers.

## Coordinates and the sampler contract

- Cell space: `x, y` in [-1, 1], **y up**. Keep shapes inside |x|,|y| < 0.9. The kit clamps at
  0.93 and fades the glow at 0.97 to leave padding, so frames never bleed into each other.
- `frame(i, n)` runs once per drawing: precompute that drawing's primitives there. It returns
  `sampler(x, y, s)`, which runs per pixel.
- Layered defs set `s.d` (silhouette, negative inside), `s.c` (core region SDF; the kit also
  insets it by `coreInset`) and `s.k` (cut lines: negative = remove mid there, so the rim
  colour shows through).
- Def options: `rim` (rim width in cell units, ~0.03–0.05), `glow` (halo radius, ~0.12–0.22),
  `coreInset`, and `grid` (2 or 4).
- Mask defs (`layered` off) set `s.d` and optionally `s.v` (grey value for shaded props).

## Primitives

| Helper | Use |
|---|---|
| `tongue(x, y, bx, by, ang, h, r1, r2, bend, wave)` | tapered capsule from a base along angle `ang` (0 = up, clockwise +). `r2 = 0` gives a sharp tip; `bend` makes a C-curve; `wave` an S-curve. Flames, spikes, rays, shards |
| `circle` | lobes (smoke, dome) |
| `smin(a, b, k)` | merge with a fillet. Small k (0.03–0.04) keeps cusps between lobes; larger (0.07–0.09) gives tongue roots |
| `fit(drawing, k, ground)` | shrink a drawing inside its cell around a ground line |
| `NA..ND`, `fbm` | **boil only**: domain warp offset by the drawing index, erosion thresholds, cut-line contours. Never use noise as the shape itself |

## Patterns that read as anime

| Want | Recipe |
|---|---|
| Fire mass | `smin` of 6–8 lobes around a dome, plus 7–10 tongues leaning up and out with per-drawing bend boil; flat ground cut `max(d, -0.9 - y)` |
| Core | the same shape function evaluated at ~55% scale toward the base (`blastShape(x/k, ...) * k`) |
| Pinch-off | for selected tongues, shrink `h` over time and add a detached small tongue at the old tip that keeps rising |
| Interior linework | `s.k = |fbm - 0.5| - 0.013`, kept away from edges (`max(k, d + 0.1)`) and out of the core |
| Cel smoke | union of lobe circles with small smin; crease lines where two lobes overlap (`|d2 - d1| - 0.011`); core = lobes shifted toward the light; dissolve with round holes that grow |
| Crescent slash | polar SDF: outer radius R, inner R − T(u); `T(u)` peaks at 60–75% toward the head; the angular SDF must be **negative inside** the arc range; streaks via `s.k` arcs; tail recedes; dashes via `sin(sv * 46)`; needle shards |
| Fire slash | crescent plus tongues rooted on the outer edge, angled back against the swing, with boil warp; burn-out via fbm erosion |
| Glint | 4 long arms + 4 short diagonals; sizes per drawing 0.45 → 0.95 → 0.65 → 0.3 |

## Review

`node paint.mjs <def>` writes the PNGs plus `out/textures/_preview_<def>.png`, which shows the
4 layers tinted with a fire, steel or smoke test palette. Debug a sampler in node with
`vm.runInNewContext(paint.js)` and print `s` at a few points. That is how the slash bug
(an angular SDF clamped to 0) was found.
