---
name: roblox-anime-vfx
description: Design, preview and export stylized anime VFX for Roblox (JJK, One Piece, Demon Slayer look) - explosions, sword slashes, impacts, auras. Hero elements are drawn headless as 4 stacked WHITE flipbook layers (glow, rim, mid, core) colored per ParticleEmitter, previewed in a three.js emulator of Roblox particles, shown to the user as a 3D viewport artifact, and exported as PNGs + Luau ModuleScripts. Use whenever the user asks for Roblox VFX, particle effects, anime effects, slashes, or wants to iterate on one.
---

# Roblox anime VFX

Goal: effects that look like a frame from a JJK / One Piece fight and build in Roblox from real
ParticleEmitters. There is no Studio here, so everything renders headless:

```
craft/textures.py (python, numpy/scipy) --> out/textures/*.png   white glow/rim/mid/core sheets + white sprites
effects/*.js  parts + combos  --build.mjs--> lint -> out/lab.html (all combos + parts, PNGs embedded)
                                            out/<Combo>/<Combo>.lua, out/parts/<Part>.lua
headless.mjs -> out/<Name>/sheet.png contact sheets;  out/lab.html --Artifact--> 3D viewport
```

| File | Role |
|---|---|
| `vfx/craft/craft.py` | Headless photo-craft: anisotropic streak noise, smudge/motion blur, levels, POLAR warp (paint a strip, bend it into a crescent), twirl, supersampling, white-layer split |
| `vfx/craft/textures.py` | Every texture recipe (`python3 craft/textures.py [names]`), with tinted `_preview_<name>.png` boards |
| `vfx/engine/spec.js` | `stack()` (4 aligned emitters per hero), `steps()`/`flicker()`, `part()` + `compose()` (combos stack parts by time/offset/scale) |
| `vfx/engine/sim.js` | Roblox ParticleEmitter emulator (sequences, shapes, rotated parts, orientation, flipbooks, LightEmission) |
| `vfx/engine/luau.js` | Spec -> self-contained Luau ModuleScript |
| `vfx/engine/lint.mjs` | Roblox rule checks + stack alignment checks |
| `vfx/viewer/` | Lab page: effect switcher, transport, layer solo, per-layer toggles, textures + Luau tabs |
| `vfx/effects/references.js` | 24 standalone parts + 3 combos (CosmicStrike, FireworkBurst, KatanaFlurry) recreating the user's clips |
| `reference/anime-research.md` | Research guide: shape language, timing, life, color, slash + explosion anatomy |

## Setup (once per container)

```bash
cd vfx && npm install   # three@0.147.0 for headless rendering (CDNs are blocked here)
pip install scipy       # photo-craft needs numpy + scipy + Pillow
```

## Workflow

1. **Break the effect into beats** (see the 5-beat table) and decide the **hero drawing(s)**:
   the one or two shapes the eye reads (blast, slash, smoke). Everything else is secondary
   sprites (sparks, glints, licks, puffs) and "life".
2. **Paint the texture** in `craft/textures.py`: a function `fn(i, cell) -> intensity image` (or
   `(alpha, value)`), registered in `RECIPES` as `layered` (split into 4 white layers by soft
   thresholds) or `single`. Read `reference/texture-recipes.md` first. **Never draw vector
   polygons/ribbons for hero art**: the user rejected that as "a 2 year old vs a pro".
3. **Paint + review**: `python3 craft/textures.py <name>`, then read `out/textures/_preview_<name>.png`
   and compare it **side by side** with a crop of the reference frame. Check it
   against the drawing checklist below before touching the effect spec.
4. **Write PARTS, then COMBOS** in `effects/<file>.js`. A reference clip is many VFX stacked on top of
   each other: make each element a standalone `part({...})` (previewable alone), then
   `compose(base, [{ part, t, at, scale, tag }])` stacks them into the clip. Heroes use
   `...stack(...)` / `planeStack(...)` with per-layer Color / LightEmission / Transparency.
5. **Build + lint**: `node build.mjs` (lints all effects, writes `out/lab.html` and the `.lua` files).
6. **Review headless**: `node headless.mjs <Name> sheet [t1,t2,...] [env]` and read
   `out/<Name>/sheet.png`. Use `shot <t>` for the full page. Do at most 2–3 tuning passes.
7. **Publish** `out/lab.html` with the Artifact tool to the **same URL** every time (pass `url`
   if the path changed). Ask for feedback by effect, layer name or beat time.
8. **Commit** the specs, `paint.js`, `out/textures/*.png`, `out/lab.html` and `out/*/*.lua`. Sheets are gitignored.

## Target style: Roblox battlegrounds VFX (user's reference clips)

The user rejected flat cel cartoon shapes with thick outlines ("generic slop"). The approved
target is the look of top Roblox battlegrounds games, recreated in `effects/references.js`:
- **Light is built from strokes, not fills.** Energy crescents are a white-hot band on the
  cutting edge plus 40–60 tapered hair strands that spiral inward. The glow is a blurred copy of
  the strands, never a gradient blob.
- **Contrast comes from black ink.** Jet-black calligraphic crescents with needle tips, hooks and
  barbs, black hairlines and black spike bursts, drawn with LightEmission 0 between additive layers.
- **Graphic accents:** navy serrated blades with white comb teeth and **manga screentone**, a
  navy 4-point star with a white rim, lens glints with long thin rays, bokeh dots, small
  yellow-green flecks.
- **Soft media stays soft:** mist, dust and haze are noisy, low-opacity, slow and behind everything.
- **3D wrap:** many arcs on different planes around the character (`planeStack` with fixed
  rotations, clustered within ~±30° of facing the camera). Edge-on arcs read as fat white rods, so avoid them.
- **Value control:** additive layers saturate to white fast. Keep mid LightEmission ~0.35–0.5,
  core Brightness ≤ 2, glow Transparency ≥ 0.5, and Bloom ~0.6 at threshold 0.9. Check that
  blue (or pink or orange) mid-tones survive in the busiest frame.
- **Ground matters:** sprites centred low get cut flat by the floor. Keep big sprites' bottom edge above y = 0.
- **Match the environment of the reference** (anime sky over a dark checker floor, or a night arena) via `stage.env`.

When the user gives reference videos: extract frames with ffmpeg (`fps=4–10` contact sheets via
`tile`, plus a few full-res crops), list every element and its texture traits, then recreate
**element by element**. Review your headless sheet side by side with the reference frames.

## Four white layers (the core technique)

Each layered drawing exports `<def>_glow`, `<def>_rim`, `<def>_mid` and `<def>_core`. All four
are white plus alpha, and the emitter `Color` does the colouring. `stack()` / `planeStack()`
emit them as aligned emitters.

| Layer | How the brush engine builds it | Typical emitter setup |
|---|---|---|
| glow | blurred copy of the body marks (per cell, no bleed) | LightEmission 1, Transparency 0.5–0.9 with stepped flicker |
| rim | body marks drawn wider by `rim` | dark ink or deep hue (LightEmission 0–0.3), or white for a white outline on navy |
| mid | body marks | main hue, LightEmission 0–0.5 |
| core | `hot` marks at `coreW` width + `coreOnly` marks (teeth, tone, highlights) | white, LightEmission 1, Brightness 1.2–2 |

Stack rules (lint enforces them): no envelopes on Size, fixed Lifetime / Speed / Rotation /
RotSpeed, SpreadAngle 0, point emitter.

## Drawing checklist (preview board)

- [ ] Strokes taper to needle points; widths vary a lot (hairlines next to bold bands).
- [ ] Energy shapes are bundles of strands with gaps, not solid crescents.
- [ ] Every effect has a black-ink element and a white-hot element. Contrast comes from value, not outlines.
- [ ] Animation over 16 cells: quick draw-on (2–3 cells), hold, then the tail recedes, strands thin and flecks peel off.
- [ ] Nothing reaches the cell edge (the engine clips at 3% padding; soft glows must fade before it).

## Life

Stepped flicker on glow and core, glints at 20–35/s while the effect holds, bokeh, flecks and
sparks, and light bumps. Fireworks use paired emitters: streaks (VelocityParallel, short) plus
twinkling dots (Random flipbook, longer, slight gravity).

## Feedback -> change

| User says | Change |
|---|---|
| "more impact / punchier" | longer or extra impact frame, bigger Flash Size, more shake `amp`, brighter core on the first drawing |
| "too floaty / slow" | shorter hero Lifetime (fewer s per drawing), higher Drag on secondaries |
| "can't read it / too fast" | add hold drawings in `paint.js` (repeat the full pose), lengthen Lifetime |
| "too glowy / looks like Roblox" | raise glow Transparency, fade glow earlier, lower core LightEmission |
| "looks generic / slop" | fix the drawing, not the emitter: sharper tips, cusps, size hierarchy, cut lines, pinch-off |
| "no life / static" | add glints, stepped flicker, licks at 12 fps, light bumps |
| "different color" | change only the stack Colors (textures are white) |
| "bigger / smaller" | scale the stack `Size` and part sizes together |

## Roblox gotchas

See `reference/roblox-mapping.md`. Main points:
- A slash on a plane = `rotation` on the layer (the part's CFrame.Angles) + `EmissionDirection`
  Top + `Orientation` VelocityPerpendicular + Speed 0.01. The in-plane angle comes from `Rotation`.
  Check the in-plane angle in Studio, because Roblox's reference axis may differ from the emulator's.
- Upright billboards that sit on the ground: `FacingCameraWorldUp`, with the emitter at
  `Size × 0.45` height when the drawing's ground line is at y = -0.9.
- Impact frames, Highlights and shake are client-only: call `Play()` on every client.
- Upload the PNGs listed in `out/<Name>/textures.txt`, then paste the ids into `TEXTURES` in the `.lua`.
