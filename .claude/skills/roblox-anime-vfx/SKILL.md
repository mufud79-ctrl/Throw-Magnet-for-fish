---
name: roblox-anime-vfx
description: Design, preview and export stylized anime VFX for Roblox (JJK, One Piece, Demon Slayer look) - explosions, sword slashes, impacts, auras. Hero elements are drawn headless as 4 stacked WHITE flipbook layers (glow, rim, mid, core) colored per ParticleEmitter, previewed in a three.js emulator of Roblox particles, shown to the user as a 3D viewport artifact, and exported as PNGs + Luau ModuleScripts. Use whenever the user asks for Roblox VFX, particle effects, anime effects, slashes, or wants to iterate on one.
---

# Roblox anime VFX

Goal: effects that look like a frame from a JJK / One Piece fight and build in Roblox from real
ParticleEmitters. There is no Studio here, so everything renders headless:

```
engine/paint.js --paint.mjs--> out/textures/*.png  (white glow/rim/mid/core flipbooks + white sprites)
effects/*.js    --build.mjs--> lint -> out/lab.html (all effects, PNGs embedded) + out/<Name>/<Name>.lua
                 headless.mjs -> out/<Name>/sheet.png contact sheets for self-review
out/lab.html    --Artifact--> 3D viewport the user scrubs and comments on
```

| File | Role |
|---|---|
| `vfx/engine/paint.js` | Headless "paint" kit: SDF drawings (tongues, lobes, arcs) split into 4 white layers |
| `vfx/engine/spec.js` | `stack()` (4 aligned emitters per hero), `steps()` + `flicker()` (stepped NumberSequences) |
| `vfx/engine/sim.js` | Roblox ParticleEmitter emulator (sequences, shapes, rotated parts, orientation, flipbooks, LightEmission) |
| `vfx/engine/luau.js` | Spec -> self-contained Luau ModuleScript |
| `vfx/engine/lint.mjs` | Roblox rule checks + stack alignment checks |
| `vfx/viewer/` | Lab page: effect switcher, transport, layer solo, per-layer toggles, textures + Luau tabs |
| `vfx/effects/` | `fire_explosion.js`, `sword_slashes.js` (SwordSlash + FireSlash). Copy their structure |
| `reference/anime-research.md` | Research guide: shape language, timing, life, color, slash + explosion anatomy |

## Setup (once per container)

```bash
cd vfx && npm install   # three@0.147.0 for headless rendering (CDNs are blocked here)
```

## Workflow

1. **Break the effect into beats** (see the 5-beat table) and decide the **hero drawing(s)**:
   the one or two shapes the eye reads (blast, slash, smoke). Everything else is secondary
   sprites (sparks, glints, licks, puffs) and "life".
2. **Draw the hero** in `engine/paint.js` as a function `frame(i) -> sampler(x, y, s)` that
   sets `s.d` (silhouette SDF), `s.c` (core SDF) and `s.k` (cut lines). Register it with
   `layered: true`. Read `reference/texture-recipes.md` and `reference/anime-research.md` first.
3. **Paint + review the drawing**: `node paint.mjs <def>`, then read
   `out/textures/_preview_<def>.png`, which tints the 4 layers with a test palette. Check it
   against the drawing checklist below before touching the effect spec.
4. **Write the spec** in `effects/<file>.js`. Each hero is `...stack(base, { glow, rim, mid, core })`
   with per-layer Color / LightEmission / Transparency.
5. **Build + lint**: `node build.mjs` (lints all effects, writes `out/lab.html` and the `.lua` files).
6. **Review headless**: `node headless.mjs <Name> sheet [t1,t2,...] [env]` and read
   `out/<Name>/sheet.png`. Use `shot <t>` for the full page. Do at most 2–3 tuning passes.
7. **Publish** `out/lab.html` with the Artifact tool to the **same URL** every time (pass `url`
   if the path changed). Ask for feedback by effect, layer name or beat time.
8. **Commit** the specs, `paint.js`, `out/textures/*.png`, `out/lab.html` and `out/*/*.lua`. Sheets are gitignored.

## Four white layers (the core technique)

Each hero drawing exports `<def>_glow`, `<def>_rim`, `<def>_mid` and `<def>_core`. All four are
white plus alpha, so the ParticleEmitter `Color` does all the colouring and you can recolour
without new textures. `stack()` makes 4 emitters on one point with identical motion, so they
line up exactly in Roblox.

| Layer | What the alpha is | Typical emitter setup |
|---|---|---|
| glow | stepped halo around the silhouette (3 hard steps) | LightEmission 1, Transparency 0.4–0.6 with a stepped flicker; **fade it out before the dissolve** |
| rim | the full silhouette; reads as the outline plus interior cut lines | darkest saturated hue (crimson/navy), LightEmission 0 |
| mid | silhouette inset by `rim` width, minus cut lines | main hue, LightEmission 0–0.2 |
| core | hot region (its own SDF, inset from the edge) | near-white, LightEmission 0.3–0.5, Brightness 1.6–2.5 with a stepped flicker |

Stack rules (lint enforces them): no envelopes on Size, fixed Lifetime / Speed / Rotation,
SpreadAngle 0, point emitter. Only colour, transparency, LightEmission, Brightness and ZOffset
may differ between layers.

## Drawing checklist (preview sheet)

- [ ] Thick-to-thin everywhere; tips end in points. Convex lobes meet at sharp cusps (smin k ≤ 0.04).
- [ ] One dominant mass, a few medium shapes, many small bits. No equal-sized blobs, no noise blobs.
- [ ] The shape changes between drawings: boil (domain warp offset per drawing), tongues bend, tips pinch off.
- [ ] The dissipation is drawn into the frames (holes, dashes, shards, pinch-off), not done with a transparency fade.
- [ ] Nothing touches the cell edge; use `fit()` to shrink a drawing that clips.
- [ ] The core is the silhouette's shape at ~55% scale, sunk toward the base or along the cutting edge. It is not separate dots.
- [ ] Rim is visible as an outline at sprite size. Shapes thinner than ~2× the rim width turn into dark seeds, so make them bigger or drop them.

## Life (what separates good from generic)

Even a "still" element must move. For every hero add:
- **Stepped flicker** on glow and core Transparency: `steps(flicker(base, amp, 8–9, seed), fadeTo)`.
- **Glints**: 4-point `glint` flipbook (2x2 OneShot, 0.12–0.22 s) at 6–35/s around the hero while it holds.
- **Sparks**: needle `spark` with VelocityParallel. Use a burst on the hit, then a trickle via `rate`.
- **Boil**: the hero drawing itself plus `flame_lick` sprites in Random mode at 12 fps.
- **Light**: a PointLight brightness track with small stepped bumps, not one smooth fade.

## The anime look (rules)

Full notes: `reference/anime-research.md` (research) and `reference/anime-style.md` (per-series).
- Flat cel bands with a dark rim; LightEmission 1 only on glow, sparks, glints and lines.
- Timing: hits on 1s, most drawings on 2s (12 fps → Lifetime = 16/12 s for a 4x4), smoke on 3s (8 fps).
- Fast in, hold, slow out: big Speed + high Drag for secondaries; the hero drawing holds 2–4 drawings at full size.
- Impact frames: 1–3 frames of white, B/W threshold and red tint (`impactFrames`), plus shake.
- Slash: appears at **full length in one drawing** (thin smear first), thickest at 60–75% toward
  the leading tip, then thins from the inside → streaks → dashes and shards.
- Explosion: flash star → lumpy dome with tongues → hold → tips pinch off → smoke takes over from the edges.

### 5-beat structure

| Beat | Typical time | Layers |
|---|---|---|
| Anticipation | 0–0.3 s (slash: 0–0.1 s) | gather lines, charge or tip glint |
| Impact | +0–0.13 s | impact frames, flash star, speed lines, shake |
| Bloom | +0.03–0.3 s | hero stack, licks, rings |
| Hold | +0.3–0.6 s | hero holds and boils, glints, sparks, embers |
| Erode | +0.6–2 s | hero dissipation frames, smoke hero, dust, scorch |

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
