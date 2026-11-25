# Dragon fruit (hybrid + full form): working notes (branch claude/dragon-fruit-vfx-k354ta)

Brief: `prompts/dragon_fruit_session.md`. Design: `lab/dragon/DESIGN.md`.

## Layout
- `lab/dragon/kit.py`       per-fruit kit (fire palette, layer conventions, helpers), from `lab/thunder/kit.py`
- `lab/dragon/moves/*.py`   one script per move -> `dragon_NN_Name.json`
- `assets/renders/dragon/`  MP4s + strips shown to the user
- Export (after all approved): `python3 scripts/export_luau.py --effects lab/dragon/moves`

## Status
| step | status |
|---|---|
| 1. research + design doc | v1 shown; user redirected: wingless Eastern dragon emperor (v2 block in DESIGN.md) |
| 2. concept sheet | full form v3 APPROVED ("Full looks good"); hybrid v4 (house cel style of the thunder god sheet, blocky R15, T-pose, no fingers) waiting for approval |
| 3. Meshy model + rig (wings) + rig layer v2 | - |
| 4. fire matter | - |
| 5. hybrid Z X C V B F | - |
| 6. full form Z X C V B F | - |
| 7. second pass | - |
| 8. export + manifest | - |

## Step 1: research
~60 videos' auto-frames (vfx-reference-frames). Takeaways in DESIGN.md section 1. Key: Type Soul fire on sand =
saturated gold body + crimson rim (no white-out), crescents with torn tongues; black smoke is the dark anchor of
every fire blast; dark dragons with lava seams read best; breath needs rolling billows + ember spray + ground
splash/scorch, never a clean cylinder; tornado = spiral bands.

## Credits
| item | estimate | spent |
|---|---|---|
| Figma concept image | 1-2 images | 9 images (sheet v1, hero v2, sheet v2, hero v3, sheet v3, hybrid v1, hybrid v2, hybrid v3, hybrid v4), gpt-image-2.5-flare |
| Meshy multi-image-to-3D (dragon v3) | 30 | 30 (1989 -> 1959) |
| Meshy multi-image-to-3D hybrid v4 (all pieces in one job, avatar masked out) | 30 (was ~120 for 4 crops) | 30 (total 60) |

## Step 2: concept (direction change)
User: "as close to Kaido as possible while still being original enough", "should look more like Kaido". Pulled 24
reference videos (scratchpad only). v1 sheet = generic wingless lizard-serpent (superseded). v2 hero = broad bulbous
nose, spiral-carved brow, toothy grin, long whiskers, curl mane, helmet horns, belly band, S-coil body, in
obsidian/ember/crimson/gold. No IP names in prompts or files. v2 sheet's side-view head is narrower than the hero's:
push it toward the hero when modelling. Next-session prompt: prompts/dragon_vfx_session.md.

## Step 2b: v3 colours + hybrid
User: "Change colors to match Kaido, make design cooler, hybrid = additions to the normal R15 model". v3 = azure/teal
scales, cream belly, cream-gold horns, navy curl mane, scar, second horn pair, fire in the throat. VFX stays fire-
coloured (orange on blue = contrast). Hybrid sheet: blocky R15 with horns, curl collar, scale shoulder plates, scale
forearm sleeves + talon gauntlets, tail. Pieces weld to R15 parts.

## Step 2c: hybrid v2
User: "Full looks good, hybrid looks okay, hybrid should have fingers and the look should be more aggressive overall".
hybrid_r15_v2.png: hooked horns + spike crest, flame-point curl collar, spiked pauldrons, bladed forearms, 5-finger
claw hands (skinned, finger bones), back spine ridge, spiked tail with a blade tip. Still R15 add-ons.

## Step 2d: hybrid v3
User: "too round, blocky R15 won't work, should be T-posed, NO FINGERS, just cool hybrid stuff". hybrid_r15_v3.png:
faceted low-poly hard-surface pieces (horns, shard collar, spiked pauldrons, bracers with blade claws, back blades,
segmented angular tail). Build in Blender, no Meshy. Lesson: R15 add-ons must be boxy/faceted to match the body.

## Step 2e: hybrid v4 (house style)
User: "Wrong style completely, follow style guide from the lightning model". House style = C_tpose_sheet_v3.png: 2D
anime turnaround, ink lines, cel shading, strict T-pose, ornate gold trim + crimson tassels. hybrid_r15_v4.png:
horns + crown band, curl collar, dragon-head pauldrons, scale bracers with claw blades, crimson-gold sash, curl-fan
tail. RULE: every character/model sheet uses this house style (never 3D renders or low-poly looks).

## Step 1: model (waiting for approval)
Session prompt: prompts/dragon_vfx_session.md (branch claude/dragon-vfx-rigging-animation-5h3r0p). Scope of this
session (relayed user update): steps 1-3 only (model, hybrid pieces, rig, rig layer v2 + exports). Moves are done by
the "Dragon fruit VFX moves" session (prompts/dragon_vfx_moves_session.md).
- Dragon: Meshy multi-image-to-3D from v3_view_side/top/front (padded to 1024 squares), 30 credits.
  Raw: assets/source_art/meshy/dragon_v3.glb. Views: assets/source_art/dragon/meshy_raw/raw_head.jpg, raw_body.jpg.
  Head, horns, curl mane, whiskers, grin, legs and tail fan all read. Issues to fix in the rig script: the tail thins to
  a stalk before the fan (thicken), a stray cream lump on the back above the rear legs (delete).
- Hybrid crops from hybrid_r15_v2.png were made but never submitted: obsolete (v2 rejected).
- Hybrid v4 (user idea: mask the avatar out of the sheet, ONE job, split the pieces in Blender): the front/side/back
  views of hybrid_r15_v4.png with the shirt/pants/face box/box hands masked out (meshy_raw/make_hybrid_inputs.py ->
  meshy_raw/hybrid_v4_inputs.png), Meshy multi-image-to-3D, 30 credits. Raw: assets/source_art/meshy/dragon_hybrid_v4.glb.
  Views: meshy_raw/hybrid_raw.jpg, hybrid_closeups.jpg. Pieces come out as separate islands: horns+crown, collar +
  dragon-head pauldrons + bracers with claw blades (one band, to split per R15 part), sash with medallion/tassels, tail
  with spines and curl fan. The horns read lumpy from the side.
