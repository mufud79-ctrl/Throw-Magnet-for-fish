# Handoff: Thunder fruit + Raijin god mode (roblox-anime-vfx)

Branch: `claude/ecstatic-mayer-950cm0`. Skill: `.claude/skills/roblox-anime-vfx/` (read `SKILL.md` and `references/` first).
This is the first fruit built to the "design first, user approves everything, then bake" process. The earlier
100-move batch (`lab/effects`, `assets/renders`) was rejected as samey templates; do not reuse its approach.

## How the user wants to work (non-negotiable)
- Show everything before baking/exporting: concept images, reference sheets, raw models, textures, each rendered
  move. Wait for approval. Use artifacts or SendUserFile with images (clicking local paths does not open files).
- Every move must have its own mechanic and signature visual. No shared "impact recipe", no filler wisps,
  no templated staging. Follow the five animation rules (anticipation, squash/stretch, follow-through,
  timing/hit-stop, arcs).
- Textures greyscale first (recolourable), then tinted. Painted, multi-layered, not vector-looking.
- Mesh budgets in polygons; Roblox cap is 20k triangles per mesh.
- Commit + push after each step.

## Approved so far
1. **Style rules** (all approved): lightning is instant (1-2 frame strikes, motion from flicker + cooling
   afterglow); colour script white -> cyan #6fe0ff -> blue #3a5cff -> indigo #2a1a9a afterglow, storm navy
   #2a3350 anchors, gold #e8b44a and crimson #d23a48 only on the god; angular zig-zags (30-60 deg kinks, long
   straight runs); a dark anchor in every move; hit-stops 0.04-0.08 zaps, 0.12-0.18 pillars, one inverted
   impact frame on big hits; Lichtenberg burn scars on the ground as the fruit's calling card.
2. **Base moveset** (approved, original names):
   | Move | Key | Mechanic | Signature visual |
   |---|---|---|---|
   | Volt Lance | Z | instant hitscan throw | lightning spear lingers on the line + burn scar |
   | Thunderclap | X | close-range stun | spherical cage of arcs; arcs crawl on stunned enemies |
   | Judgment Pillar | C | placed delayed strike | storm cloud telegraph with inner flashes, colossal multi-strand column, crater |
   | Flash Step | V | teleport dash | body becomes a bolt on a 3-kink zig-zag path, flickering ribbon, re-form burst |
   | Thunder Serpent | B | heavy weaving projectile | serpent of chained lightning ribbons on an S-curve, painted head, coils and bursts |
   | Static Field | N | lingering zone | crawling ground arcs, floating static, random bolts jump up every 0.5 s |
   | Plasma Bomb | M | hold-charge lob | chain lightning hopping between up to 3 targets |
3. **God mode "Raijin Ascension"** moves (approved): Drum Barrage (8 drums strike on a 0.12 s beat, each fires a
   bolt), Heaven's Palm (giant lightning hand slams from the sky, palm crater; reuse `palm_strike` art),
   Thunder God's Wrath (rise, drum crescendo, rain of 20 pillars, final colossal strike + impact frame).
   Beat sheets for every move are on the design review page (see links).
4. **God design**: concept C "Drum Deity" (`assets/source_art/god_mode/C_drum_deity.png`), original Raijin-style
   (not Enel's likeness or attack names). T-pose sheet v3 approved (`C_tpose_sheet_v3.png`; front/side/back
   crops `ref_*.png`).
5. **God model generated**: `assets/source_art/meshy/thunder_god.glb` (Meshy multi-image-to-3D, 30 credits).
   Raw: 1.36M tris, single mesh, one 2048 texture, cape and mane fused to the body (1,916 "loose parts" are UV
   seams). User approved the model and the cleanup/rig plan.
6. **Lightning textures approved** ("all the vfx look amazing"): `thunder_bolt` (seed 406), `thunder_burst`,
   `thunder_arc`, `plasma_orb` (redesigned), `storm_cloud` + `storm_flash`, `lichtenberg`, `scorch_burn`,
   `static_sparks`, `ion_haze`, `thunder_strip_1..4` (wrapping ribbons). Recipes in `scripts/vfx_textures.py`
   (search "THUNDER FRUIT"), PNGs in `assets/textures`, previews/GIFs in `assets/previews`.
7. **Drums float behind the current model** (no frame; do NOT regenerate the god model). 8 drums in a ring.

## Progress (session 2)
- **Drum ring approved + exported**: one connected gold horseshoe arch (user overrode "no frame"), 8 drums (crest
  between the top pair), tassels. `scripts/drum_ring.py` -> `assets/meshes/drum_ring/` (glb, blend, FBX with armature
  Root > Drum_1..8 > Tassel_1..8; drums numbered left to right over the top = Drum Barrage order). Built in god space.
  Refs: `drum_sheet_v1.png` (drum), `drum_ring_sheet_v1.png` (frame).
- **Cutscene pitch v1 approved** ("Start"): `assets/source_art/god_mode/cutscene/` (storyboard_v1.jpg, shot1..7,
  beat_sheet_v1.md): sky eye, heartbeats, one-frame strike, pour + silhouette swap, drum forge, slow-mo assembly,
  first beat scar circle. Supersedes the draft below.
- **God cleanup done**: `scripts/god_cleanup.py` -> `assets/meshes/thunder_god/thunder_god_clean.*` (Body 18k, Cape
  4k, Mane 6k tris).
- **God rig v1 (waiting on user approval, FBX not exported yet)**: `scripts/god_rig.py` -> `thunder_god_rig.blend/json`.
  R15 bone names + chains (Cape_{L,C,R}_1..4, Mane_1..6_1..3, Sash_{L,R}_1/2/Tassel, Hakama_{F,B}_1..2). Bone heat
  gave rigid torn weights on this mesh, so body weights are analytic (position bands blended across joints) +
  Laplacian smoothing. `--preview DIR` writes test-pose GLBs; `--export` writes `thunder_god.fbx`.
- Base moves (Z..M) are being built in a sub-session on branch `claude/thunder-moves-950cm0` (notes in
  `THUNDER_MOVES_NOTES.md` there). God-mode moves stay here.
- **Animations v1 (waiting on user review)**: `scripts/god_anim.py all` bakes idle, transform, drum_barrage,
  heavens_palm, thunder_gods_wrath, cast -> `assets/meshes/thunder_god/anim/*.glb` (god + ring, one clip each).
  Framework: idle as a pose function, per-bone key tracks with eases, arm/leg/torso/head/hand-shape helpers
  (armature-space axes; arms rest along X so Y = raise, Z = fore/aft, X = roll), springs on cape/mane/sash
  driven by root velocity + chest lean speed (per-bone gains small: offsets compound down chains), drum hit
  recoil, drum overrides for the cutscene forge/assembly. Previews bake hit-stops as holds; export for Roblox with
  `--no-hitstop` (the runtime adds them). Renders: `lab/anim_render.mjs` (`--target/--dist` close-ups,
  `--frame-at` framing, `--period` closed loops) -> `assets/previews/god_mode/anim/`. Rig now has 86 bones (15
  finger bones per hand; hands rebuilt at higher detail in god_cleanup `--hands`), max 4 influences per vertex.
  Reel page (all clips): https://claude.ai/artifact/FuXt8488k2xTbEQxbibkrf
- `lab/model_views.mjs` takes an optional `WxH` viewport; materials named `XRAY*` draw on top (skeleton overlays).

## Waiting on the user (original list)
- **Drum reference sheet** `assets/source_art/god_mode/drum_sheet_v1.png` (front/side/3-4 of one taiko drum:
  red lacquer, gold rims + rivets, cream skin with black/gold tomoe, gold bands). Get approval first, then model
  it in Blender (simple enough to build procedurally; or Meshy multi-image if the user prefers).
- **New transformation cutscene**: the user said the first draft was not cool enough. Pitch a much cooler one
  (storyboard frames via Figma image gen + beat sheet) and get approval before building. Draft to start from:
  1. 0.0 Low-angle slam-in close-up on the caster; world desaturates; dust and debris start drifting inward.
  2. 0.3 A storm cloud rolls across the sky in a time-lapse; distant flashes; letterbox bars slide in.
  3. 0.6 Caster levitates; arcs climb the body; strike 1 from the cloud (cut to wide, inverted impact frame).
  4. 0.85 / 1.0 Strikes 2 and 3 with micro-cuts: hand close-up, then glowing eyes close-up.
  5. 1.2 Lightning cocoon: a sphere of crawling arcs wraps him; Lichtenberg scars race outward across the
     ground; rocks lift off the ground.
  6. 1.6 Slow-motion beat (time scale ~0.3) while the camera orbits 90 degrees; the cocoon cracks like glass
     with light leaking through the cracks.
  7. 1.9 BURST: white-out + inverted frame; the god is revealed mid-air, cape billowing; drums snap into the
     ring one by one (0.08 s apart), each with a BOOM ring.
  8. 2.5 He lands: crater, shockwave, dust; all 8 drums strike at once; the storm stays overhead flashing; the
     grade returns with a cyan tint. Optional name card "RAIJIN ASCENSION".
  Roblox side: scripted camera (CameraType Scriptable) driven by spec camera keys; the previewer already
  supports camera pos/look/fov keys.

## Next steps, in order (show results after each)
1. Drum approval -> Blender drum prop (`scripts/vfx_meshes.py` style; separate parts so each drum can pulse),
   8-drum ring rig (ring root + per-drum bones).
2. God model cleanup (Blender, `/tmp/bpyenv/bin/python`): merge by distance, split into body / cape / mane by
   position + texture colour, decimate each under 20k tris (target ~15k body, 3k cape, 4k mane; texture keeps
   detail). Turntable renders: `node lab/model_views.mjs <glb> <out.jpg> 0,90,180,270`.
3. Rig: R15-compatible humanoid skeleton (Roblox Animation Editor compatible) + sway chains: cape 3 columns x 4,
   2 sash tails + tassels, front/back hakama panels, 6 mane locks. Auto weights; check deformation renders.
4. Animations: transform (new cutscene), idle (breath, cape drift, drums orbit), cast, drum strike, palm slam,
   ultimate. Bake spring secondary motion on cloth/hair chains into keyframes. Preview by exporting GLB with
   animations and rendering in three.js (extend `lab/page/model.html` with AnimationMixer).
5. Build each VFX move one at a time with the approved textures and rules (hand-authored, no templates). The
   previewer is `lab/page/vfx.js` + `lab/render.mjs` (JSON spec format in `references/spec-format.md`). It
   still lacks a true ribbon Trail type and a volumetric mesh beam: add them (both in the previewer and the
   Luau runtime `templates/ReplicatedStorage/AnimeVFX/init.lua`) before the beam/trail moves. Show each move.
6. Export: FBX for the rigged god + drums, Luau specs via `scripts/export_luau.py`, upload manifest.

## Environment notes
- Python with bpy/scipy/Pillow: `python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy scipy pillow imageio`
  (Blender 5.3; no GPU: Workbench/EEVEE renders fail; use the three.js previewer or Cycles CPU).
- `cd lab && npm install` (three@0.147.0). Playwright + Chromium are preinstalled.
- Meshy CLI: `npm exec --yes --package=meshy-cli@0.4.0 -- meshy ...`; login is per container
  (`meshy auth login --device`, user approves in the browser). Balance was ~2,019 credits. Estimate before
  spending; text-to-3D preview ~20, multi-image textured ~30.
- Figma image gen: file "Anime VFX source art" (fileKey `axlni9pqaU8SvqL9jopFIu`, user's Pro team); create a
  session first; download PNGs immediately (links expire in 7 days). Prompts that worked are in this file's
  history; key rules for model sheets: strict T-pose, palms down, open hands, gaps at armpits and legs, cape
  clear of legs, neutral closed mouth, no VFX/clouds/held items; mirror front/back views for symmetry but
  mirror the head on the face's own axis (see `C_tpose_sheet_v3.png`).
- YouTube blocks headless playback with a CAPTCHA; don't bypass it. Use `i.ytimg.com/vi/<id>/maxres{1,2,3}.jpg`
  frames for reference.

## Links (private to the user)
- Thunder design review (style, moveset, beats, god plan, textures): https://claude.ai/artifact/L1Fg5WqxsjCCKkLiUPhMcR
- Texture library gallery: https://claude.ai/artifact/H5dB95EVh3qM6Sb6TTx6VL
