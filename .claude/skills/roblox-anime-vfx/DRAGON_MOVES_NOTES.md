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
| Figma concept image | 1-2 images | 9 images (sheet v1, hero v2, sheet v2, hero v3, sheet v3, hybrid v1, hybrid v2, hybrid v3, hybrid v4), gpt-image-2.5-flare |
| Meshy multi-image-to-3D | 30 (cap 60) | - |

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
