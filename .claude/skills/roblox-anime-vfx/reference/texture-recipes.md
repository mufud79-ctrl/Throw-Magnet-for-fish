# Texture recipes (vfx/craft, headless photo-craft)

Pro Roblox VFX sprites are painted in an image editor, not drawn as vectors. `craft.py` recreates
that workflow in numpy/scipy, so the textures are smooth and painterly with no stamps or polygons.

## Core moves

| Move | Function | Use |
|---|---|---|
| Paint a straight strip (u along, v across) | numpy grids | every slash, swoosh, trail, blade, ink stroke |
| Pressure taper | thickness profile `T(u)` (sin-based, peak toward the head) | needle tips at both ends |
| Streak texture | `noise(h, w, sy, sx)` with sy tiny and sx long + `levels` | hair streaks inside energy |
| Smudge | `mblur(I, sigma, axis)` along the stroke | silky motion |
| Organic edges | domain-warp the strip with low-frequency noise | no ruler-straight edges |
| Bend it | `polar(strip, size, r_out, r_in, a0, sweep, vtop, spiral)` | crescent / swoosh / blade |
| Twirl | per-row wrap-around roll of a 360° strip + wrap blur | vortex, ground swirl, ring slash (seamless) |
| Radial | 360° polar with v = radius, `spikes_profile` along angle | shard nova, eruption, ink spikes, radially smeared fire |
| Analytic glows | exp falloffs (core + rays) | glint, flare, line, spark, bokeh, orbit ring |
| Supersample | paint at 2x, Lanczos down | clean edges |
| Layer split | `split(I, glowSigma, thresholds)` | white glow/rim/mid/core with soft transitions |

Threshold sets: `E` for painted energy (soft gradient white → hue → deep edge); `B` for graphic
shapes painted with a flat body at 0.36 (rim = thin fringe, mid = flat body, core = teeth, tone, ridges).

## Recipes that match the references

| Texture | Recipe |
|---|---|
| `wisp_arc` (energy swoosh) | 6 feathery tongues per arc, each a tapered band whose tip flicks outward (v < 0); white-hot outer edge, streak noise, domain-warped edges, tail breaks into streaks |
| `trail_arc` (wind) | the same with 4 tongues, thinner and less white |
| `ink_arc` | one black crescent, belly toward the head, needle tips, dry-brush hair split on the tail, 2 inward spurs, spiral 0.12 |
| `saw_fan` | curved blade with a sawtooth outer edge (26 long teeth), flat navy body, white teeth, screentone dots |
| `rift` | horizontal tear: spiky top and bottom profiles around a wobbling centre line, lit top edge |
| `energy_swirl` | 360° strip of streaks + soft clouds, twirled, wrap-blurred: a cosmic vortex |
| `shard_nova` / `shard_fan` | spike length profile in polar space; lit side where the profile rises |
| `fire_burst` | spiky radial heat field + noise, smeared radially |
| `star4` | concave astroid `|x|^0.42 + |y|^0.42 < 1` with ridge highlights and a hot centre |

## Review

Always crop the reference frame and put it next to `_preview_<name>.png` (PIL). Judge silhouette,
edge quality, gradient and streak texture, not just the shape.
