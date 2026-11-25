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
