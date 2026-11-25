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
| Figma concept image | 1-2 images | 11 images (+ sheet v4, hybrid v5) (sheet v1, hero v2, sheet v2, hero v3, sheet v3, hybrid v1, hybrid v2, hybrid v3, hybrid v4), gpt-image-2.5-flare |
| Meshy multi-image-to-3D (dragon v3, superseded by v4 sheet) | 30 | 30 (1989 -> 1959) |
| Meshy multi-image-to-3D hybrid v4 (one job, avatar masked out; superseded by hybrid v5 kitbash) | 30 | 30 (total 60) |
| Meshy multi-image-to-3D (dragon v4 open-mouth re-run, user OK'd) | 30 | 30 (total 90) |
| Meshy multi-image-to-3D dragon v5 body + head (2 jobs, user OK'd "Yes") | 60 | 60 (total 150 this session) |

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

## Step 2f: model sheet v4 (open mouth, feet, thicker body)
User on the raw Meshy dragon (from v3): "feet look really off", and "should have the image with an open mouth so you
can rig it easier". dragon_sheet_v4_openmouth.png: jaw dropped ~40 deg in side + front views (teeth, red interior,
tongue modelled, so the jaw bone only has to close it), a THICK body tapering into a tail that stays thick into the
curl fan, strong legs with clear joints, clean feet (3 forward toes + 1 back toe, one big ivory talon each) + a foot
close-up. Meshy inputs: v4_view_side/top/front.png (+ v4_view_foot.png for reference). Re-run ~30 credits.

## Step 2g: hybrid v5 from dragon pieces
User: "Looks good (sheet v4), make sure the hybrid matches the new references and uses pieces of that dragon model".
hybrid_r15_v5.png: horns, mane-curl collar, mini open-mouthed dragon-head pauldrons, body-sleeve bracers with
talons, spine ridge, tail with curl fan. All kitbashed from the one dragon mesh and texture, with no Meshy jobs for
the hybrid. The crown and sash are dropped.

## Step 1: model (v3 raw + hybrid v4 raw both superseded; v4 dragon re-run next)
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

## Step 1b: dragon v4 re-run (waiting for approval)
- User: hybrid v5 "needs full redesign" -> chose "Becoming the dragon" (partial transformation: scale plates creep up
  from the hands, talon gauntlets, horns breaking out, short thick tail, fire in the skin-to-scale seams). Sheet next.
- Dragon v4: Meshy multi-image-to-3D from v4_view_side/top/front, 30 credits (total 90). Raw:
  assets/source_art/meshy/dragon_v4.glb. Views: meshy_raw/v4_body.jpg, v4_head.jpg, v4_feet.jpg.
  Open mouth with red interior, fangs and tongue modelled (rig the jaw to close). Body much thicker; strong jointed
  legs. Weak spots: talons are small; the tail still narrows into a thin neck right before the curl fan (thicken in
  rig_dragon.py); whiskers come out as 3-4 strands per side (pick 2 per side or merge).
- Hybrid v6 concept "becoming the dragon": assets/source_art/dragon/hybrid_r15_v6.png (Figma gpt-image-2.5-flare,
  1 image, file "Anime VFX source art"). Scale plates swallow the arms with 3-claw talon gauntlets (no fingers), scales
  climb the neck and back of the head, horns + back pair burst out, a glowing spine ridge, a short thick curl-fan tail
  off the ground, molten fire cracks where skin turns to scale. Waiting for the user's verdict.
- User: "Hybrid is base form, just the horns and tail, no arm stuff, no back stuff, just the horns and some scales."
  -> DESIGN.md "Revision v5": horns + tail + a few scale patches, all kitbashed from dragon_v4.glb. v5 and v6 sheets dropped.
- Meshy audit (user asked): balance 1989 -> 1749 today = 240 spent. This session: 90 (dragon v3, hybrid v4, dragon v4).
  The other 150 (a v3 dragon multi-image + 4 image-to-3d jobs, all at 15:25 UTC) were not submitted by this session;
  the timing matches the duplicate session. Rule from now on: no Meshy job without the user's explicit OK in this chat.
- User on dragon v4: "looks like shit", "should be longer, rn it looks like a snake with huge legs versus a Chinese
  dragon". Free prototype (scratchpad lengthen.py): trunk x2.6, tail x2.4, cross-section x1.4, legs x0.6, S-curve.
  Proportions read more like a Chinese dragon, but the stretched texture smears the scales and belly band. Asked the
  user: keep the stretch (fix texture later) vs a new long-body sheet + Meshy re-run (needs explicit OK).
- User: "New model, rn the head and smaller details look like shit, keep that in mind for new image gen, it needs hella
  polish". Cause: in a 1536-px strip the head is ~250 px, so Meshy gets mush. New plan: two sheets, two Meshy jobs,
  joined in Blender. dragon_sheet_v5_long.png (long serpentine body, small legs, straight side + top) and
  dragon_head_sheet_v5.png (head only, full frame, side/front/top, bold simple shapes, mouth open, 2 whiskers, 8 big
  mane curls). Figma gpt-image-2.5-flare, 2 images. Polish in Blender: clean 2-strand whiskers, symmetrize, bigger
  talons, emissive eyes, teeth/horn cleanup. Waiting for the user's OK on the sheets + ~60 Meshy credits.
- Dragon v5 (user OK'd): body job (b5 side+top crops) + head job (h5 side/front/top, segmented clean, target 50k)
  = 60 credits. Raw: meshy/dragon_v5_body.glb, dragon_v5_head.glb; views meshy_raw/v5_head_raw.jpg, v5_body_raw.jpg.
  Head is a big step up (clean curls, brow spirals, eyes, fangs, 2 whiskers). scripts/build_dragon.py joins them:
  front legs slid back 0.10 (they sat under the mane), placeholder head cut at y -0.66, new head x0.25 seated so the
  mane swallows the neck stub, both textures packed into one 2048 atlas (one TextureID).
  Out: meshy/dragon_v5_assembled.glb, view meshy_raw/v5_assembled.jpg. Polish still to do: shoulder smear from the leg
  slide, tail fan is flatter than the sheet, talons small.
- User: "Head is wayyyy too big" (0.25). build_dragon.py: --head-scale default 0.15, placeholder remnants above the neck removed (cut + z>0.07 band + loose islands found on position-welded connectivity, since glTF splits verts on UV seams). Sizes compared in meshy_raw/v5_head_sizes.jpg (A 0.18, B 0.15, C 0.12).

## Step 2: rig + base animations (waiting for approval)
User: "0.18 good, start rigging; idle animation, movement animation, M1 animation".
- scripts/rig_dragon.py (on build_dragon.assemble, head 0.18): in head space the Meshy whiskers are cut (below the chin,
  in front of the jaw, strands crossing the mouth, any saturated whisker-blue below the nose) and replaced by 2 clean
  procedural tapered whiskers (1 per side); the modelled OPEN jaw (split on the bisector of the lips, hinge falloff)
  is rotated shut 46 deg and baked, so rest = closed and `jaw` keys open it (same as the serpent). Head 9.5k + body
  8.5k tris (11k looked shard-like) -> 18.7k tris, smooth shaded, 30 studs, head along glTF -Z.
  Bones (35): spine_00 (head) .. spine_19, jaw, legFL/FR/BL/BR_0/1 (L = -X), whiskerL/R_0..2.
  Out: assets/models/dragon.glb + dragon.json, assets/meshes/dragon.fbx.
- Rig layer v2 in the previewer (lab/page/vfx.js): `follow: "rigid"` (root rides path/move/wave, `orient` keys
  [[t, [x,y,z] deg]] seconds, Euler YXZ) or path (as before); `boneTracks` {bone: {rot: [[t,[x,y,z]]], loop, offset,
  mirror: ["L","R"]}} local Euler XYZ added on top of the follow pose; every bone resets to rest each frame.
  Bone axes: spine local Z = yaw, +X bends the body behind the bone down; orient +X = head up.
- lab/dragon/anims/ (anim_kit.py, idle.py, movement.py, m1.py) -> dragon_idle (4 s loop, rigid hover, travelling S
  ripple, breathing jaw, whisker drift, leg paddle), dragon_movement (path-follow fly-by, S-weave + vertical
  undulation, banking roll, legs tucked, whiskers streaming), dragon_m1 (bite lunge: rear + gape, lunge, snap at 0.42
  with hit-stop 0.06 + shake, tail ripple, settle). Renders: assets/renders/dragon/dragon_{idle,movement,m1}.mp4.
- Not done yet: Luau side of rig layer v2 (task 4), hybrid pieces (horns + tail + scales), small whisker wisps left
  beside the jaw.
