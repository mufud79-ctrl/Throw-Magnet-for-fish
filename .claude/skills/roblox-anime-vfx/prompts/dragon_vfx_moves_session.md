First run: git fetch origin claude/dragon-fruit-vfx-k354ta && git merge --no-edit FETCH_HEAD
Then build the Dragon fruit's actual VFX: the fire matter and all 12 moves. Use the same bar and the same loop as
the thunder fruit (the user called the modern pass "so much better").

## Read first (non-negotiable)
1. `.claude/skills/roblox-anime-vfx/SKILL.md`, `references/modern-vfx.md` (the 10 failure modes),
   `references/move-workflow.md`, `references/spec-format.md`.
2. `THUNDER_MOVES_NOTES.md` (every rejected attempt and why) and `lab/thunder/kit.py` + `lab/thunder/moves/*.py`
   (the template for a hero fruit: hand-written, one script per move).
3. `lab/dragon/DESIGN.md`. The revision blocks at the top (v3d, v3c, v3b, v3, v2) override the body: the dragon
   is a wingless Eastern serpent dragon emperor (azure scales, cream belly, cream-gold horns, navy curl mane,
   whiskers), and the hybrid is add-on pieces on the blocky R15 player. The move swaps are Horn Rush and Firestorm
   Coil, the transform coils out of the cocoon, and the revert coils and collapses. Sections 1-2 (research, fire
   matter, palette, layer conventions, calling card) and section 4 (beat sheets) are the VFX spec.
4. `DRAGON_MOVES_NOTES.md`: status, lessons and credit log. Keep it updated.

## The VFX language (from DESIGN.md)
- Fire colour script: white-gold #fff4c8 -> gold #ffc23a -> orange #ff7a1a -> crimson #d4202a -> ember red
  #8a1418 -> char #2a2226. Orange fire against the blue dragon is the contrast that sells it.
- Layer conventions: core white-gold LE 1 (thin); mid gold LE 0.4; rim crimson LE 0.2, which covers the sand and
  cools to char; glow orange LE 0.75 at about 70% transparency.
- Dark anchor: billowing black smoke on every big fire shape, plus scorch. No dark outlines around glow.
- Calling card: claw gouges (claw moves) and molten cracks (slams) burned into the sand. They glow white-gold,
  cool to charcoal, and drift embers.
- Grades: warm dim for hybrid moves; a deep warm dim for the full form that holds while the dragon exists.
- Reference look on sand: Type Soul fire, which is a saturated gold body with a crimson rim, crescents with torn
  tongues, and fire washes that roll along the ground. A breath must be a torrent (rolling billows, an ember
  spray, a ground splash and scorch), never a laser.

## Steps (show me each one and wait for my approval; send MP4s, frame strips and contact sheets with
## SendUserFile, strips <= 8000 px; commit and push after each step on the branch this session is assigned)
1. **Fire matter.** Paint the new greyscale sheets in `scripts/vfx_textures.py`. They are layered
   (`_glow/_rim/_mid/_core`), 4x4 flipbooks unless noted, and painted rather than vector: `flame_billow`,
   `flame_tongue`, `flame_strip_1..4` (tileable along U, they scroll), `claw_rake` (three parallel burning
   crescents), `fire_crescent`, `fire_ring` (flat), `fire_impact`, `molten_crack` (flat, calling card),
   `claw_gouge` (flat, calling card), `heat_ring`. Re-tint `smoke_cel_v3` charcoal for black smoke; reuse
   `embers` and `lava_drops`. Preview with `texture_preview.py` and send me a contact sheet plus tinted fire
   previews. Wait for approval before building moves on them.
2. **Kit.** Write `lab/dragon/kit.py` from `lab/thunder/kit.py`: the fire palette, HOT/COOL per layer, `_modernize`
   with the fire conventions, the warm-dark grade in `write()`, and fire versions of the helpers (impact, shockwave,
   streaks, sparks, smoke3 in charcoal, dust_ring, rocks, crack -> molten_crack, gouge, embers, flame_wash,
   billow). These are plumbing only: every move's staging is hand-written in its own script.
3. **Rig and models.** If the rigged dragon (`assets/models/dragon.glb`) and the hybrid pieces don't exist yet,
   use stand-ins so the VFX isn't blocked. The dragon stand-in is `thunder_serpent` tinted azure, which takes
   the same path-follow rig layer. The hybrid stand-in is the plain previewer avatar, plus simple Blender
   stand-in meshes if a move needs a tail or claws to read. Keep the model names in the specs swappable. If the
   rig layer v2 features a move needs (`follow: "rigid"`, `boneTracks`, bone-riding emitters, the `attach` layer)
   are missing, add them in BOTH `lab/page/vfx.js` and `templates/ReplicatedStorage/AnimeVFX/init.lua`. Keep the
   Luau parse-checked with luaparse, and say that it hasn't been run in Studio.
4. **Hybrid moves**, one at a time (`lab/dragon/moves/<move>.py` -> `dragon_NN_Name.json` via `kit.write()`):
   Z Talon Rend, X Horn Rush, C Sky Drop, V Tail Cyclone, B Ember Breath, F Transform. For each:
   `cd lab && node render.mjs dragon/moves/<spec>.json --hd --out out/dragon`, dense strips around the beats
   (`scripts/strip.sh`), and a review against the modern-vfx checklist. Fix it until it passes, then send me the
   MP4 and strips and wait.
5. **Full-form moves**, one at a time the same way: Z Inferno Torrent, X Comet Dive, C Firestorm Coil, V Dragon
   Roar, B Ash Rain, F Revert.
6. **Second pass** on all 12 together: same style, none whiter or busier than the rest, a consistent colour
   script, the calling card on every move. Send a side-by-side.
7. **Export** (only after everything is approved): `python3 scripts/export_luau.py --effects lab/dragon/moves`, then
   update `assets/upload_manifest.json` (textures, meshes, rig models). Do NOT upload anything.

## Rules
- Each move has its own mechanic and signature shape, in one visual language for the whole fruit. No shared
  impact recipe, no templated staging, no `scripts/effects.py` archetypes.
- All five animation rules on every move (anticipation, squash and stretch, follow-through, timing and hit-stop,
  arcs). Hit-stops are 0.04-0.08 for small hits and 0.12-0.18 for big ones, starting about 1 frame after the
  strike. One flash per beat (1-2 frames). Only Sky Drop, Transform, Inferno Torrent and Comet Dive get an
  inverted or mono impact frame.
- Every hit has a BIG / medium / small hierarchy plus mass (black smoke, a dust ring hugging the ground, rocks, the
  animated mark).
- PointLight brightness <= ~8 equivalent. Ground decals at y 0.06-0.1 with ZOffset >= 0. Radial ground rings use
  Cylinder / Surface / Outward, never Disc.
- Original design: no names, logos or signature attacks from any existing IP.
- Meshy or Figma image generation only if a move truly needs a new asset. Estimate first and report the spend.
