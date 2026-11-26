# Dragon fruit (hybrid + full form): working notes (concept: claude/dragon-fruit-vfx-k354ta; VFX: claude/dragon-fruit-vfx-moves-zkkcp7)

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
| 4. fire matter | 14 sheets painted, contact sheet sent, waiting for approval |
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

## VFX session (branch claude/dragon-fruit-vfx-moves-zkkcp7)
Ownership (user, relayed from the coordinating session): this session owns the VFX (fire matter, kit, 12 moves,
second pass, export). The "Dragon VFX rigging and animation" session owns the dragon model, the hybrid pieces, the
rig and rig layer v2 in lab/page/vfx.js + templates/ReplicatedStorage/AnimeVFX/init.lua. **Do not edit the rig layer
code here.** Moves use stand-ins (thunder_serpent tinted azure; the plain previewer avatar) with swappable model
names; rig v2 gaps go in this file and get swapped in once the rigging branch is pushed.

Moveset change (user: "rip moves straight from the anime", "no club"): full Z = a detonating blast breath, full V =
Rending Gale wind blades, full C = a wind twister that ignites. Own names, no club. DESIGN.md revision v4.

### Step 1: fire matter (waiting for approval)
`scripts/vfx_textures.py` "DRAGON FIRE MATTER": explicit layers (not pc.split) so the white-gold core stays thin:
rim = whole silhouette (crimson LE 0.2), mid = gold where heat > threshold with alpha shaded by the painted volume
(lobe shadows show crimson), core = hottest pockets / leading edges only, glow = tight + wide halo. `cool` raises the
thresholds so the core dies first and the rim lingers for the emitter to cool to char.
Sheets: flame_billow, flame_tongue, flame_strip_1..4 (1024x256, tile in u, tongues lean toward -u), claw_rake,
fire_crescent, fire_ring (flat), fire_impact, molten_crack (flat), claw_gouge (flat), fire_slice (flat, new for
Rending Gale), heat_ring. Black smoke = smoke_cel_v3 tinted #2a2226; reuse embers + lava_drops.
Review tool: `scripts/fire_preview.py` (Roblox LightEmission blend with the kit's conventions, dark + sand, hot and
cooled) -> assets/previews/dragon/.
Fixes during review: molten_crack went white once the core was gone (pool radius 0 -> smoothstep(0,0) = 1; guarded);
first cracks were thin (read as lightning) then a starfish (too few fat trunks) -> 8 uneven trunks with 3 branches;
billow too small and cooled too early; tongue tear didn't read (now an explicit pinch); impact star spikes were
hairlines and the burst had a centre-dot artefact (inner edge at r=0).

### Composition pass: "looks good individually, unpolished combined" (user, after the first Talon Rend render)
Diagnosis from full-size frames, and the fixes (kit-level, so every move gets them):
1. **Cooled crimson rims read as flat red paper cut-outs.** The rim kept full opacity after the gold body eroded and
   cooled toward char. Fix: rim colour cools to ember red only (char is the ground decals' job), and `_modernize`
   gives every one-shot rim RIM_FADE (thins out over the second half of its life). Glow halo a bit stronger (62%).
2. **No light interaction.** The previewer's PointLights (decay 2) barely light anything, so characters and sand
   never reacted to the fire. Fix: `glow_pool` (soft additive pool on the sand under every fire source) and
   `glow_orb` (soft glow riding hands / throats), on new single-image `soft_glow` texture. (orb_glow_glow is a 4x4
   flipbook: used as a single image it drew a grid of 16 dots. Never use a flipbook sheet with FlipbookLayout None.)
3. **No connective tissue between beats.** Elements popped on and off independently. Fix: continuous flame ribbons on
   the claws between strikes, `ambience` embers drifting through the area for the whole move.
4. **Single-frame pile-ups.** Impact + flare + 22 random streaks + rake on the same 2 frames = noise. Fix: streaks only
   on the big beat, fewer, aimed along the strike; the smoke enters a beat after the fire.
5. **Black smoke as a dirty blob on the target's face.** Fix: smoke placed behind and above, translucent (tr 0.3),
   fades in, rises, ZOffset -0.8.
6. **Weak grade.** Saturated blue sky competed with the fire. Fix: hybrid (-0.17, +0.15, #ffd8b4), full (-0.27, +0.2,
   #ffc4a0).
7. **Staging.** The camera pushed in behind the caster (the avatar blocked the rakes) and the lunge overlapped the target.
   Fix: side three-quarter camera at ~14 studs, rakes on the camera side of the target, shorter lunge.
8. Inward "suck" embers read as polka dots -> converging spark_streak needles.

## Move 1: Talon Rend (hybrid Z) - built, composition pass done
`lab/dragon/moves/talon_rend.py` -> `dragon_01_TalonRend.json`. Stand-in: plain avatar (no hybrid pieces; claw fire
rides the hands through `kit.hand()` FK until rig v2 `attach` exists - GAP for the rigging session).

### Fluidity pass (user: "stiff and boring, needs to be fluid, hands need a flame trail"; "it's an ability, not a cutscene")
- Poses: `kit.smooth()` Catmull-Rom control keys resampled at 60 Hz: arms swing on arcs with overshoot and settle, the
  torso leads each swing (overlap). Linear 3-key snaps read stiff.
- Claw trails: three flame trails per hand riding the three claw tips (`hand_path(..., lateral=, fwd=)`), 0.26 s life,
  hot head cooling along the trail: the swipe is DRAWN by the motion.
- Camera: one fixed gameplay view for every move (`GAMEPLAY_CAM`: behind, above, right of the caster, FOV 70).
  No cinematic cameras: these are abilities. Light shakes on hits only.
- Filler matter (new, all moves): fire_wisp, fire_swirl (loop), flame_flicker (loop), ember_burst, smear_arc,
  gust_lines, heat_haze (loop), smoke_wisp, ash_flakes + kit helpers wisps / swirl / flicker / ember_spray / smear /
  gusts / haze / smoke_wisps / ash. Rule: every beat gets filler (swirl on charge, smear on swing, spray on hit, wisps
  and after-smoke after), so no frame is only the big shape.

### Anime cel pass (user: "could look more anime to fit our style")
`_fire_layers` FIRE_CEL mode (default on; FIRE_CEL=0 paints the soft v1): crisp silhouette, hard-edged gold body with
ONE flat shadow band (mid at 50% over the crimson rim = an orange tone), a larger hard white-gold inner flame. Repainted
flame_billow, flame_tongue, flame_strip_1-4, claw_rake, fire_crescent, fire_ring, fire_impact, flame_flicker. Stroke
sheets (cracks, gouges, slice, wisps, swirl, sprays) were already crisp. New `anime_glint` (4-point star) + kit.glint.
Comparison: assets/previews/dragon/cel_compare.jpg. Wide glow trails against the sky read as pale haze blocks: keep
glow ribbons slim (<= 1.6) and translucent.

## Move 2: Horn Rush (hybrid X) - built
`lab/dragon/moves/horn_rush.py` -> `dragon_02_HornRush.json`. The wall = a wide fire_crescent laid flat on the ground
(bowing forward) + 11 standing tongues riding it (tallest in the middle, following the arc) + billows dropped behind +
a tapered flame wash; gust needles / embers / wisps / smoke stream with it. Lessons: a single camera-facing arch reads
as a vector hoop from behind; white gust_lines sprites read as vertical bars when the motion is into the screen (use
VelocityParallel needles); the camera must FOLLOW the caster (`kit.follow_cam`) - gameplay cameras track the player.
Bug fixed: `scorch()` and the calling-card char decals sampled 4x4 sheets with FlipbookLayout None (grid of 16
asterisks). New single-image `fire_scorch`; char decals play their sheet (hidden until the glow cools).

## Move 3: Sky Drop (hybrid C) - built
`lab/dragon/moves/sky_drop.py` -> `dragon_03_SkyDrop.json`. Leap rides two spiral flame ribbons (trails on a helix
around the body) with flame bursts at take-off and a mid-air boost; apex claw swirls; stretched dive with a short
fire trail; impact = mono frame + hit-stop 0.15 + crater + molten_crack + fire_ring + 16 standing flame spots that burn
down + black smoke column + after-smoke / shimmer / ash. Follow camera with y_follow 0.8 and a wider base framing
(a 16-stud leap leaves the default frame). Long-lived trails on a vertical dive read as laser lines: keep them short.

### Fused fire walls (user: "the flames look individual vs a large combined flame like real life")
Rows/rings of separate tongue particles read as candles. New `flame_wall_1..4` strips (1024x256, tile in u, TOP = tips):
composed FROM the approved cel matter like real fire - 4 big swaying flame_tongue frames dominate the skyline, medium
tongues between, small flickers in front, billow lobes fusing the base, heavily overlapped (each gold body covers its
neighbours' outlines). Two from-scratch attempts were rejected first: a flat clip-art curtain ("doesn't fit our style")
and evenly spaced flicker teardrops ("spikes, not fire"). Lesson: fire walls need a size hierarchy and an uneven skyline.
Drawn as ONE ribbon: `kit.wall_beam` (camera-facing Beams, width = wall height, three spans with tapered ends, optional
bow; flip=True puts the tips up; no glow Beam - it shows its rectangle) and `kit.ring_wall` (a vertical Trail drawn
around the circle in ~0.12 s; the curtain it leaves is the ring). Horn Rush and Sky Drop now use them.

## Move 4: Tail Cyclone (hybrid V) - built
`lab/dragon/moves/tail_cyclone.py` -> `dragon_04_TailCyclone.json`. The (virtual) tail tip draws the ring: a vertical
flame_wall Trail following the tip through the 360 spin (one continuous curtain). Eruption: 8 `kit.pillar` columns in
sequence (new `flame_pillar_1..4`: approved flame_tongue frames stacked up a tall canvas + base billows, stored as a
Beam strip, u=0 base), crowned by billows, a small fire_ring at each base, smoke and falling embers after. Rejected on
the way: vbeam torrents as pillars (flat striped planes = lasers) and tiny-radius ring_wall pillars (a trail swept in
0.05 s gets 1-2 samples and collapses). GAP: no tail mesh on the avatar (rig v2 `attach`, rigging session).

## Move 5: Ember Breath (hybrid B) - built
`lab/dragon/moves/ember_breath.py` -> `dragon_05_EmberBreath.json`. Cone = a narrow camera-facing torrent-strip Beam
core (mouth -> sweeping contact point) wrapped in billows riding three depths of the cone (small near the mouth, big at
the far end); where it touches the sand a vertical flame_wall Trail draws a continuous curtain along the 50-degree arc,
scorch fan + flickers after. GAP: no jaw mask (rig v2 attach).

### BUG (all moves): billows and fire impacts were invisible
`billow()` and `impact()` passed the ease word "out" as the 3rd element of an emitter Size sequence, where the 3rd
element is the Roblox envelope (a number) -> NaN size, nothing drawn. Fixed in the kit; all five moves re-rendered.
An opaque Beam also hides particles inside it: billows must be bigger than (or outside) a ribbon to read.
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
- User on v1 anims: "so stiff, fucking zero movement, look up how [the reference dragon] moves". Reference frames
  (vfx-reference-frames, scratchpad only): the dragon is almost never straight: it hovers in big coils/loops/figure-8s
  with the body wrapped around itself, swims in large full-body waves, and strikes by whipping the head with the body
  uncoiling behind. Rework (all three now path-follow, the rigid idle/M1 read as a stiff plank):
  idle = head circles a tilted loop (r 6.5, 5 s) so the body coils around it + ripple + head bob, roll 0 (banking read
  upside down); movement = vertical S amp 6 / wavelength 26 + lateral weave + roll into turns + 0.55 s tail whip;
  M1 = cruise in, cobra rear-up with a hang (0-0.34), whip strike at ~120 studs/s (spline velocity scale 1.6), snap
  0.46 + hit-stop 0.07, drive past, swoop up, tail crack, coil back. anim_kit: spline() (Hermite with per-key velocity
  scale: 0 = hang, >1 = whip), ripple().

## Merge: rigging session's branch (claude/dragon-vfx-rigging-animation-5h3r0p)
Merged as agreed once it was pushed: assets/models/dragon.glb (30 studs, spine_00..19, jaw, whiskers, legs), rig
layer v2 in vfx.js (rigid follow + orient, boneTracks), anims/ (idle, movement, M1). Only DRAGON_MOVES_NOTES.md and
DESIGN.md conflicted (both appended): kept both. kit.DRAGON_MODEL = "dragon"; kit.dragon() takes boneTracks.
Design change from that branch: the HYBRID is the base form (horns + tail + a few scales; no arm pieces) - the hybrid
moves' fire claws already carry the reach in VFX, as the revision v5 block asks.

## Move 6: Transform (hybrid F) - built
`lab/dragon/moves/transform.py` -> `dragon_06_Transform.json`. Cocoon = an EGG of stacked ring_walls (wide lower ring,
narrower ring, cap; `ring_wall(base=)`), re-wrapped by a bigger egg, spiral flame ribbons, billows; the player swells
to 1.25x then shrinks away inside the densest fire (hidden swap) while the real dragon pours out spiralling up (its
unborn body underground), coils, roars at the burst (inverted frame, hit-stop 0.16, billow ring, fire ring, heat
rings, smoke wall, molten crack), then swims a slow loop. Grade into_full. Gameplay camera zooms out to
GAMEPLAY_CAM_FULL as the dragon appears.

### Polish pass (user: "these need so much polish - find why it looks bad"; diagnosis vs modern Roblox fire showcases)
Diagnosis: fire read as opaque stickers (rim LE 0.2 was a thunder-on-sand rule), it lit nothing, shapes stood still
(walls / columns) instead of flowing, one focal shape was missing (clutter), black smoke read as dirt, flipbooks step.
User: no darkening ("these aren't ultimates"); the big thing is ABILITY AMBIENCE - "haze particles, dust particles,
not tiny ones, big large pieces".
Done (kit-level, every move): layer conventions glow 1.0 @ 40% / rim 0.35 / mid 0.55 / core 1 (LE 0.65 on the rim
washed the fire out to pale yellow on sand - body must stay saturated, the glow comes from the halo); grades are now a
barely-there warm tint (no darkening); glow pools 1.4x bigger; new `dust_veil` texture + `ambience()` BIG layer
(rolling ground dust veils 9-16 studs, big heat-haze sheets, large tumbling ember pieces, a high soft smoke veil) +
`dust_rollout()` (big dust veils rolling out of impacts). Sky Drop: dust rollouts, a flat whirling fire spiral at the
landing (flow shape), fewer rocks. Before/after: assets/previews/dragon/skydrop_polish_before_after.jpg.
Previewer light falloff in vfx.js left alone (no answer on touching it).

### Reference rebuild (user: "still looks like shit, doesn't look like your reference photos, keep rebuilding")
Matched against full-size reference frames (TSB / Type Soul / Roblox fire showcases, incl. Type Soul fire on sand):
1. Colour dominance flipped: GOLD-YELLOW body, orange middle, thin red edge (ours was crimson-dominant = dark, outlined).
2. Soft painted gradients again (FIRE_CEL default 0): flat cel bands + outlines read as stickers.
3. On bright ground the colour must COVER, not add: glow = deep red tint (LE 0.35, 50% transparent), rim 0.2,
   mid 0.35, core 0.9, bloom 0.38. Additive gold glow on sand = white-out (tested, rejected).
4. The flowing primary shape: `kit.fire_streams` (hot-headed flame ribbons spiralling out/in around a point, cooling
   along their length) + thin hot yellow swirl lines over them; on every move (Sky Drop landing, Talon finisher, Horn
   Rush contacts, Tail Cyclone spin + eruption, Ember Breath landing, Transform charge-in + burst-out).
5. Ambience big-piece embers were pale paper rectangles at LE 1 / size 1.3 -> deep orange, LE 0.5, 0.85.
All six hybrid moves re-rendered.

### Type Soul pass (user: "still not even close, you're listing reasons, not executing them")
Compared against Type Soul fire ON SAND (the right reference for our arena): huge flat saturated YELLOW cel masses,
thin orange-red edges, giant swirling yellow vortex discs + solid crescent arcs around the character, sharp dark-red
spikes radiating from hits, torn flame scraps flung out. Executed:
- palette yellow-dominant (mid #ffd21a, rim #ff6a10, core #fff6b0, glow #ff8a14); named colour constants remapped;
  LE glow 0.3 / rim 0.15 / mid 0.25 / core 0.6 (flat colour covers the sand); FIRE_CEL back to 1 (flat cel bands).
- new `spike_burst` texture + `kit.dark_spikes`; `kit.fire_scraps`; `kit.fire_bloom` (huge 2-layer ground glow,
  volumetric translucent flame mass, solid yellow crescents sweeping around, sustained hot heart).
- Sky Drop: big flat yellow vortex (fire_swirl x2), bloom, spikes, scraps. All six moves got bloom/spikes/scraps on
  their main beats. Comparison: scratchpad reference_vs_ours_v3.jpg (not committed: contains YouTube frames).

### Honest reset (user: "still so mid, the moves all look the same, lock in, research, be brutally honest")
Research (VFX Apprentice / League VFX style guide, particlefx.studio timing-shape-colour guides, 80.lv, VSQUAD
interview). The expert "recipe for a bad effect" - stack additive elements, max every parameter, as many particles as
possible, no hierarchy, trigger everything at once - described exactly what I had built. Brutal findings:
1. SHARED RECIPE: fire_bloom + fire_streams + dark_spikes + fire_scraps + shockwave + glint + ember_spray on every move
   = every move looked the same (it broke the brief's "no shared impact recipe" rule). Removed from every move; each
   keeps ONE lead shape: Talon = claw crescents, Horn Rush = moving wall, Sky Drop = vortex + ring (spikes only here),
   Tail Cyclone = crown of pillars, Ember Breath = cone + scorched fan, Transform = cocoon -> burst ring.
2. NO VALUE STRUCTURE: the grayscale test showed yellow fire on tan sand has the SAME luminance as the sand - the
   effects vanished in grayscale. Rule: on light backgrounds change value, not hue. The rim is now a dark crimson
   alpha-blended edge (LE 0): dark edge / bright yellow body / near-white core - 3 value steps (as Type Soul does).
3. Ambience halved (big layer is filler, not the subject).
Gray/colour grids: assets/previews/dragon/six_moves_{color,grayscale}.jpg. Still weak (next): Talon finisher too
small, Ember Breath cone small, Transform burst reads small at gameplay distance, timing still long in places.

### Anime rework (user: "I want anime stylized VFX - look up anime Roblox VFX, tell me why you made this, rework it")
Mesh-led test (swirl/crescent/ring/dome/tube with colour textures) was REJECTED ("even worse"): round, soft, static
shapes. Studied anime Roblox VFX (Spirits Reborn on sand, green energy hit, ink splash, fire slam): SHARP pointed
tapered shapes (flame spikes, needles, shards, 4-point star sparkles), directional energy (radial speed lines, needles
streaking out), flat hard-edged saturated colour with white highlights and BLACK/dark accent shapes, lots of small
crisp sparkles, instant pop timing. Everything I had built was round and soft (billows, blobs, ribbons, cylinders)
and static. New sprites: anime_flame_spike, anime_slash, ink_shards, speed_burst, needle_bold (+ anime_glint).
Sky Drop impact rebuilt with strict hierarchy: PRIMARY crown of 22 flame spikes; SECONDARY speed lines + black and gold
ink shards + star flash (+1 frame); TERTIARY gold needles, popping star glints, scraps, dark spikes; MASS dark smoke
behind, molten cracks, dust. Frames: assets/previews/dragon/skydrop_anime_rework.jpg. Waiting for the user's verdict
before converting the other moves.
