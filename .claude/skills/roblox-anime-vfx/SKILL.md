---
name: roblox-anime-vfx
description: Make Roblox anime combat VFX in the style of RELL Seas (One Piece-style fruit moves, haki, sword slashes, beams, slams, auras, ultimates). Paints recolourable greyscale textures headlessly (photocraft), builds VFX meshes in Blender (Meshy and Figma image generation for organic hero assets), authors moves as JSON specs that follow the five Disney animation rules, previews them as rendered video without Roblox open, and exports them to a Luau runtime. Use for any Roblox VFX, particle, ability, skill or move effect request.
---

# Roblox anime VFX (RELL Seas style)

Everything here runs headless. The loop is: **paint or reuse assets -> author a move spec -> render it -> review the
frames honestly -> fix -> show the user -> export to Luau.** The previewer and the Roblox runtime play the same
JSON, so what you show is what ships.

## Quality bar (read first)

The target is "you can't tell it from RELL Seas". Before showing anything, compare against
`references/rell-look.md`. Most common failures, in order:

1. **Generic textures forced onto every element.** Each element needs its own painted matter (fire billows, molten
   jets, faceted ice, inky void tendrils, electric arcs, water jets). Paint what the move needs.
2. **Vector look.** Flat fills, perfect circles, hard uniform lines. Textures must read as painted by a person:
   internal light and shadow, soft-but-defined edges, multiple layers. Never fake brush-stroke stamps.
3. **White-out.** Too many additive layers and white cores bloom pale elements (light, ice, quake, thunder,
   blade, water) into identical white blobs. Keep palettes saturated; white only in small hot cores.
4. **No animation.** Particles without the five rules feel dead. See below; every move must use all five.
5. **Same staging for every element.** Beams, dashes and projectiles need element bodies (spear, ice shard,
   molten fist, chained bolts, flying crescents, water spiral), not one white bar.

## The five rules (every move, no exceptions)

1. **Anticipation:** caster winds up and leans back while energy gathers inward; the charge orb pinches before
   release. (`charge()`, `pose_throw()`)
2. **Squash & stretch:** projectiles stretch along velocity (VelocityParallel + Squash); bursts and shells squash
   flat on contact, then stretch (`SQUASH_HIT`, non-uniform shell scale keys); targets squash on the hit.
3. **Follow-through:** caster overshoots and settles; trails lag (drag, longer life); the burst keeps flying along
   the travel direction; smoke drifts after. (`follow_through()`)
4. **Timing:** hit-stop on every hit (`spec.hitstop`): effect time freezes 0.03-0.16 s; impact frames flash at the
   start of the freeze; shake keeps running.
5. **Arcs:** projectiles curve (`move.arc`), sparks and debris fall on gravity, damage numbers pop and arc.

Details and the Roblox implementation of each: `references/animation-rules.md`.

## Workflow

1. **Name the move** (element + archetype) and write its beat sheet: wind-up, release, travel, hit (+ hit-stop),
   follow-through, settle, with times.
2. **Assets.** Reuse the library first (`references/texture-library.md`, mesh kit in
   `references/assets-pipeline.md`). If the move needs new matter, paint it greyscale in
   `scripts/vfx_textures.py` (layered = 4 white layers, or shaded = greyscale value + alpha), preview it
   (`texture_preview.py`), and **show the user the texture gallery before building moves on it**
   (`gallery.py` -> publish as an artifact). Colour comes from the emitter, never the PNG.
3. **Author** the move in `scripts/effects.py` (kits + archetypes + building blocks), or hand-write a spec
   (`references/spec-format.md`).
4. **Render**: `node lab/render.mjs lab/effects/<name>.json --out lab/out` -> mp4, contact sheet, poster.
   Pull dense frame strips with ffmpeg around the beats and review them critically against the quality bar.
5. **Show the user** the rendered videos (publish a gallery artifact; they can't open local files by clicking).
6. **Export**: `python3 scripts/export_luau.py` -> `templates/ReplicatedStorage/AnimeVFX/Effects/*.lua`,
   `Assets.lua`, `assets/upload_manifest.json`. Runtime setup: `references/roblox-runtime.md`.

## Commands

Python with numpy/scipy/Pillow/bpy lives in `/tmp/bpyenv` (create: `python3 -m venv /tmp/bpyenv &&
/tmp/bpyenv/bin/pip install bpy scipy pillow imageio`). Node + Playwright are preinstalled; `cd lab && npm install`.

| Step | Command |
|---|---|
| Paint textures | `/tmp/bpyenv/bin/python scripts/vfx_textures.py [name ...]` |
| Texture previews + GIFs | `/tmp/bpyenv/bin/python scripts/texture_preview.py [name ...]` |
| Texture gallery page | `/tmp/bpyenv/bin/python scripts/gallery.py OUT_DIR [updated,names]` |
| Mesh kit (Blender) | `/tmp/bpyenv/bin/python scripts/vfx_meshes.py [name ...] --no-render` |
| Meshy hero -> quads | `/tmp/bpyenv/bin/python scripts/retopo_hero.py [name] --polys 3500` |
| Generate move specs | `python3 scripts/effects.py [--only Flame,Ice]` |
| Render moves | `node lab/render.mjs lab/effects [--out lab/out]` |
| Export to Roblox | `python3 scripts/export_luau.py` |

## Hard rules

- Textures are greyscale/white so one PNG serves every colour. Layered textures ship as `_glow/_rim/_mid/_core`.
- Stacked layers are separate Roblox emitters and **cannot share random numbers**: stacks use deterministic motion
  (fixed speed, rotation, lifetime, no spread). Randomise only single-texture emitters (sparks, smoke, embers).
- Mesh budgets are **polygons** (quads): VFX shells <= 2,500 polys, hero meshes <= 4,000 (Roblox caps uploads at
  20,000 triangles). Scripts can't set `MeshPart.MeshId` or `DoubleSided`; shells are double-sided in geometry and
  played through `SpecialMesh` (FileMesh) so Scale can be tweened.
- Effects are client-side; the server validates and broadcasts (`FireAllClients`); damage never waits on VFX.
- Uploading assets is the user's call (it's public-facing and moderated): hand them `assets/upload_manifest.json`.
- Meshy and Figma image generation cost credits: estimate first (Meshy `make --dry-run`), keep it to what the move
  needs, report what was spent.
- The Luau was structurally parsed (luaparse) but has not been run in Studio unless the user confirms it; say so.

## Files

```
SKILL.md                     this file
references/                  rell-look, animation-rules, spec-format, texture-library, assets-pipeline, roblox-runtime
scripts/photocraft.py        headless painting kit (noise, domain warp, heightfield shading, polar warp, layer split)
scripts/vfx_textures.py      the texture library (recipes + registry)
scripts/texture_preview.py   tinted composites, flipbook GIFs, board
scripts/gallery.py           texture review page for the user
scripts/vfx_meshes.py        Blender VFX mesh kit
scripts/retopo_hero.py       Meshy GLB -> watertight all-quad Roblox mesh
scripts/effects.py           element kits x archetypes -> 100 move specs (the five rules live here)
scripts/export_luau.py       specs -> Luau modules + Assets.lua + upload manifest
lab/                         three.js Roblox VFX emulator + Playwright/ffmpeg renderer
templates/                   Luau runtime, server/client/demo scripts, Rojo project
assets/textures|meshes|source_art|previews
```
