---
name: roblox-anime-vfx
description: Design, preview and export stylized anime VFX for Roblox (JJK, One Piece, Demon Slayer look) - explosions, slashes, auras, beams, impacts. Effects are written as specs using real ParticleEmitter properties, previewed in a headless three.js emulator of Roblox particles, shown to the user as a 3D viewport artifact, and exported as PNG textures + a Luau ModuleScript. Use whenever the user asks for Roblox VFX, particle effects, anime effects, or wants to iterate on one.
---

# Roblox anime VFX

Goal: effects that look like a frame from a JJK / One Piece fight scene and that build in Roblox
from real ParticleEmitters. There is no Studio here, so the pipeline renders headless:

```
vfx/effects/<effect>.js  --build.mjs-->  out/<Name>/<Name>.html  --Artifact-->  3D viewport in chat
   (Roblox props)            (lint)              |                                 (user feedback)
                                       headless.mjs sheet/export
                              contact sheet PNG · textures/*.png · <Name>.lua (ModuleScript)
```

| File | Role |
|---|---|
| `vfx/engine/sim.js` | Roblox ParticleEmitter emulator (sequences, shapes, orientation, flipbooks, LightEmission blend) |
| `vfx/engine/textures.js` | Procedural cel textures; one source for the preview and the PNG upload |
| `vfx/engine/luau.js` | Spec -> self-contained Luau ModuleScript (emitters, timing, lights, impact frames, shake) |
| `vfx/engine/lint.mjs` | Roblox rule checks (keypoints, enums, ranges, perf) |
| `vfx/viewer/` | Viewport page: transport, scrubber, layer solo, textures + Luau tabs |
| `vfx/effects/fire_explosion.js` | Reference effect. Copy its structure for new effects |

## Setup (once per container)

```bash
cd vfx && npm install          # three@0.147.0 for headless rendering (CDN is blocked here)
```
Playwright + Chromium are preinstalled; `headless.mjs` loads them with `createRequire`.

## Workflow

1. **Break the effect into beats** before writing anything (see the 5-beat structure below). Name
   the anime reference for each layer in its `ref` field; the user reads these in the Layers panel.
2. **Write the spec** in `vfx/effects/<snake_name>.js`. Every key in `props` must be a real
   ParticleEmitter property. Need a new texture? Add a generator to `textures.js` (see
   `reference/texture-recipes.md`).
3. **Build + lint**: `node build.mjs <snake_name>`. Errors abort; fix them, don't bypass.
4. **Review headless** before showing the user:
   - `node headless.mjs <Name> textures` and read `out/<Name>/texture_sheet.png` when textures changed.
   - `node headless.mjs <Name> sheet [times] [env]` and read `out/<Name>/sheet.png`.
     Default times cover the whole timeline; pass beat times to zoom in (`0.36,0.45,0.5,...`).
   - Check against the review list below. Do at most two tuning passes, then show the user.
5. **Publish** `out/<Name>/<Name>.html` with the Artifact tool. Republish the **same file path** on
   every iteration so the user keeps one URL. Tell the user to scrub, use ¼× speed, and Solo
   layers, and to give feedback by layer name or beat time.
6. **Iterate**: translate feedback with the table below, bump `version`, rebuild, re-check the
   sheet once, republish.
7. **Export** once the user approves: `node headless.mjs <Name> export` writes
   `out/<Name>/textures/*.png` and `out/<Name>/<Name>.lua`. Commit spec + out/ (not the sheets).

## The anime look (rules)

Full notes with per-series references: `reference/anime-style.md`.

- **Flat, not glowy.** Most layers use `LightEmission` 0–0.25 and `LightInfluence` 0. Only
  lines, sparks, rings and the core get `LightEmission` 1. Glowing additive soup is the
  "default Roblox VFX" look we are avoiding.
- **Hard cel bands + ink rim.** Textures use 3–5 hard color steps, never gradients, with a dark
  crimson or black rim. Put a dark backing layer (`ink_spike`, `ZOffset` negative) behind the
  bright fire for the outlined anime silhouette.
- **Timing is everything: fast in, hang, slow out.** Huge `Speed` with high `Drag` (5–9) gives the
  "pop then freeze" of an animated explosion. Grow `Size` 70% of the way in the first 15–20% of life.
- **Animate on 12s.** Flipbooks with `FlipbookMode` Random at 12 fps make flames "boil" like
  hand-drawn fire. Use OneShot erosion flipbooks for dissipation: puffs break into holes and
  islands, they don't fade out.
- **Impact frames sell the hit.** 1–3 frames (each ~0.03–0.05 s): white flash, then a B/W
  threshold (ColorCorrection Saturation -1, Contrast 9) with a black void, then a red-tinted
  frame. Characters get Highlight fills (white, then black).
- **Anticipation before the release.** Lines sucked inward (Sphere, ShapeInOut Inward) plus a
  charging core for 0.2–0.3 s.
- **One silhouette.** Puffs must overlap into one mass (big Size, low Speed spread, ShapePartial
  ~0.6 for ground blasts) instead of reading as separate bubbles.
- **Smoke is cel too.** Greyscale cel clusters tinted with a ColorSequence: fire-lit orange first,
  then a cool purple-grey. Drawn behind the fire (`ZOffset` -2 or lower).

### 5-beat structure (adapt per effect)

| Beat | Typical time | Layers |
|---|---|---|
| Anticipation | 0–0.3 s | gather lines, charge core, light ramp |
| Impact | +0–0.13 s | impact frames, flash star, radial speed lines, camera shake |
| Bloom | +0.05–0.3 s | core, main billows, flame licks + ink backing, shockwave rings |
| Hang | +0.3–0.6 s | drag-stalled fire, embers arcing, debris |
| Erode | +0.6–2 s | erosion flipbooks, cel smoke, afterburn, scorch decal fading |

## Headless review list

Look at every contact sheet for:
- [ ] Silhouette reads at a glance, as one mass with a clear shape (not popcorn or confetti).
- [ ] At most one bright white area per frame; the rest is flat mid-tones with ink edges.
- [ ] Impact frames are visible as separate full-screen frames (B/W and red) around the hit time.
- [ ] Nothing pokes below the ground or sideways at ground level unless intended (ShapePartial).
- [ ] Ground rings are thin lines, not filled plates.
- [ ] The tail end dissolves cleanly. No stray islands floating after ~85% of duration.
- [ ] The R15 dummy (5.2 studs) gives the intended scale.

## Feedback -> property translation

| User says | Change |
|---|---|
| "more impact / punchier" | longer or extra impact frame, bigger FlashStar Size, more shake `amp`, faster initial Speed with higher Drag |
| "too floaty / slow" | raise Drag, shorten Lifetime, pull Size keypoint earlier |
| "too fast / can't read it" | add hang: lower Drag a bit, lengthen Lifetime, add a frame hold before erosion |
| "too glowy / looks like Roblox" | lower LightEmission and Brightness, reduce bloom (`bi` in app.js), add ink backing layers |
| "flat / no depth" | more ZOffset separation, darker smoke behind, add a ring or debris for parallax |
| "bigger / smaller" | scale every Size, part.Size and Speed together (keep proportions) |
| "more like <anime>" | read that series' section in `reference/anime-style.md` and change color ramp + shape language |
| "laggy" | lower Emit counts (fewer, bigger particles), trim overlapping layers, keep < ~400 live particles |

## Roblox gotchas

See `reference/roblox-mapping.md` for exact property semantics, what the emulator approximates
(Squash, Drag model, ZOffset, sorting, bloom) and Studio-side setup. Main points:
- Shape emission needs a Part parent of `part.Size`. The exporter creates invisible anchored
  parts; a 0.05-stud part acts as a point emitter.
- A flat ground ring = `Orientation` VelocityPerpendicular + `EmissionDirection` Top + Speed 0.01.
- Impact frames, Highlights and camera shake are client-only. Call `Play()` on every client via
  `RemoteEvent:FireAllClients`, never just on the server.
- Upload textures (Asset Manager > Bulk Import), then paste the ids into `TEXTURES` in the `.lua`.
  Roblox moderation can take a minute before the ids render.
