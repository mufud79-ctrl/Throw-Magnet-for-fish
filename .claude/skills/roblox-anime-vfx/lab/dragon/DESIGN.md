# Dragon Fruit (hybrid + full form): design doc

Status: **v3 (user feedback): an Eastern serpent dragon emperor, wingless, Kaido-matched colours; the hybrid is R15
add-ons. The concept look is waiting for approval.** The v3 and v2 revision blocks OVERRIDE anything below that mentions wings, half-wings or a western build.

## Revision v3b: hybrid made aggressive, with fingers (supersedes the hybrid bullet below)
User: "Full looks good" (full-form look v3 APPROVED). "Hybrid should have fingers and the look should be more
aggressive overall." New sheet: `assets/source_art/dragon/hybrid_r15_v2.png`. It's still add-on pieces on the
normal R15 body:
- **Head:** huge hooked cream-gold horns, a jagged back pair and a crest of spikes (rigid, Head).
- **Collar:** a wild navy curl mane with flame-like points (rigid, UpperTorso).
- **Pauldrons:** jagged azure scale pauldrons with curved gold spikes (rigid, UpperArm L/R).
- **Forearms:** azure scale armour with fin blades (rigid, LowerArm L/R).
- **Claw hands:** scaly azure hands with **5 jointed fingers** and long hooked ivory-gold talons, a skinned mesh per
  hand on Hand L/R. Bones `finger1..5_0/1` let the claws curl, flex and rake (bone tracks: open on wind-up,
  snap shut on the strike).
- **Back:** a ridge of jagged cream-gold spines down the back (rigid, UpperTorso).
- **Tail:** a long spiked azure tail with a cream belly and a navy curl fan with a gold blade tip, skinned, 6-7
  bones (LowerTorso).
The stance on the sheet is a look reference. Model the pieces from it in a neutral pose. The player's own face
stays.

## Revision v3: Kaido-matched colours, cooler design, hybrid = R15 add-ons (supersedes v2 colours)
User: "Change colors to match Kaido, and make design cooler. Also a hybrid form image (additions to the normal R15
model, not a different model)."
- **Dragon colours:** deep azure/teal-blue armoured scales with navy shading, a pale cream segmented belly band,
  cream-gold ridged horns and talons, a dark navy spiral-curl mane and tail fan, long blue whiskers, narrow yellow
  eyes. Cooler: a bigger, broader head, a scarred snout, a second pair of horns, a jagged spine ridge, fire
  glowing in the throat. Look: `assets/source_art/dragon/dragon_hero_v3.png`. Model sheet: `dragon_sheet_v3.png`
  (Meshy inputs `v3_view_side/top/front.png`). The v1 and v2 sheets are superseded.
- **The VFX palette stays fire** (white-gold, orange, crimson, char, with black smoke). Orange fire against the
  blue body is the colour contrast that makes the dragon pop. The calling card, the matter and the layer
  conventions in sections 2-4 are unchanged; only the dragon's own colours changed. Drop the "ember seams" glow
  on the body; use embers and fire in the throat instead.
- **Originality guardrails:** no name, logo, title, clouds-as-a-vehicle, club or signature attack from the
  reference IP. Keep the unique details (scar, the second horn pair, the curl tail fan, the fire-in-throat
  staging). The closer the likeness, the higher the takedown risk on Roblox; that's the user's call.
- **Hybrid form = add-on pieces on the player's normal R15 body** (not a replacement model):
  `hybrid_r15_v1.png` (front, side and back views: `hybrid_front/side/back.png`). The pieces are cream-gold horns
  (with a back pair) on Head; a navy curl mane collar on UpperTorso; azure scale shoulder plates on the upper arms;
  azure scale forearm sleeves with ivory-gold talon gauntlets on LowerArm and Hand (x2); and a long azure tail
  with a cream belly and a navy curl tip on LowerTorso (skinned, 5 bones). Each piece is a separate accessory mesh
  welded to its R15 part, so it follows the player's own animation. Horns and tail can be cut from the dragon
  model. The collar, shoulder plates and sleeves/gauntlets come from Meshy image-to-3D of clean crops of the
  hybrid sheet (estimate first).

## Revision v2: Eastern serpent dragon emperor (wingless)
User: "The dragon forms should look as close to [a certain wingless Eastern dragon emperor] as possible while still
being original enough." Studied about 24 reference videos of that dragon (style only, not committed). What carries
its read, and what we took:
- **Kept (genre traits):** a very long, thick, wingless serpent body that coils through the sky in big S-curves;
  four short powerful legs with huge talons; a massive broad head with a **wide bulbous nose**, a **heavy furrowed
  brow carved with spiral curls**, a **huge toothy grin**, **two long whiskers**, a **mane of spiral curls**, and
  **enormous helmet-like horns**; a **segmented light belly band** along the whole body. Its fire mode shows a dark
  silhouette in orange light with glowing eyes and sparks, which is exactly our palette.
- **Changed for originality:** obsidian-black scales with molten ember seams (not blue), a gold belly band, a crimson
  flame-curl mane, crimson whiskers and spines, gold horns with a small back pair, gold eyes, a crimson flame-shaped
  tail fin. It has no name, logo, cloud-riding or signature attacks from that IP.
- Concept art: `assets/source_art/dragon/dragon_hero_v2.png` (look) and `dragon_sheet_v2.png` (model sheet:
  straight side, top and open-jaw front views; crops `v2_view_side/top/front.png` are the Meshy inputs). v1
  (`dragon_sheet_v1.png`) was the first wingless pass and has been superseded.

**Rig impact.** It's a serpent, so the approved `rig_serpent.py` path-follow pipeline is the base: `spine_00..19`
(longer body) plus `jaw`, plus **4 short legs** (`legFL/FR/BL/BR_0/1`, bone tracks: tuck in flight, swipe, grip)
and **whiskers** (`whiskerL/R_0..2`, sway tracks). No wing bones. Rig layer v2 still adds: `follow: "rigid"`
(roar, hover), generic per-bone tracks, bone-riding emitters, and the avatar `attach` layer for hybrid pieces.
**Hybrid pieces:** horns (rigid, on Head), claw gauntlets (rigid, on hands), a mane collar (rigid, on UpperTorso),
and a skinned 5-bone tail (on LowerTorso). No half-wings.

**Moveset changes (wings removed):**
- Hybrid X **Wing Buffet -> Horn Rush**: a short charge horns-first. The same mechanic (a forward shove) and the
  same signature (a wall of flame-wind with gust lines), now driven by the head charge and a mane flare.
- Hybrid C **Sky Drop**: the leap rides a spiral of flame (two flame bursts under the feet) instead of wing beats.
- Transform: the cocoon bursts and the serpent **pours out of it spiralling upward** (path-follow birth from inside
  the cocoon, the serpent's portal trick), coils once and roars. The body's unborn part stays inside the fire, so
  nothing pops.
- Full form: hovering means the body **undulates in a slow S** (path plus wave) while the head holds aim.
- Full C **Firestorm Wings -> Firestorm Coil**: the dragon spirals up a helix around the zone, and its body whips
  the fire tornado (the tornado follows the coil).
- Full X **Comet Dive**: it climbs in a coil, tightens into a ball of coils, then dives head-first as the comet.
- Full F **Revert**: the body coils around the player and collapses into flame.
- All other moves keep their mechanic and signature. Use legs and whiskers where wings were used for anticipation
  and follow-through (talons flex, whiskers whip).

An original dragon with a hybrid moveset (horns, claws, half-wings and a tail on the player), a transformation, and
a full-form moveset where the player *is* a rigged, flying, wing-flapping dragon. The quality bar is the same as the
thunder fruit's modern pass: `references/modern-vfx.md`. Thunder lessons apply here too
(`THUNDER_MOVES_NOTES.md`).

---

## 1. What the references taught (research)

I pulled about 60 videos' published frames with the `vfx-reference-frames` skill. Queries: roblox dragon
transformation / dragon fruit rework showcases, TSB showcase, anime dragon breath, roblox fire VFX, roblox dragon
breath, JJS fire, Type Soul fire shikai, roblox flame claw, anime fire tornado, roblox meteor crater. The curated
board is `dragon_reference_board.jpg`. The downloads are in the scratchpad and are not committed. I used them for
style only and copied no names, characters or designs.

**Fire that reads on bright sand (Type Soul fire shikai, the best match for our sand arena)**
- The body is a **flat, saturated yellow-orange with a deep red/crimson rim**. The crimson rim keeps it from
  blooming into white on sand. White appears only as a thin core line on the leading edge. This is the
  thunder rule again: body layers get low LightEmission and the rim covers the sand.
- Shapes are **crescents and arcs with torn tongues on the outer edge**. They are hard-edged and have no outlines.
  The tongues tear off and fly back along the motion, so the follow-through is built into the texture.
- Big fire on the ground is a **wash**: a flat, saturated sheet rolling along the sand with tongues standing up off
  its edge. It isn't a pile of round puffs.

**Impacts and explosions (roblox fire VFX, meteor crater studies)**
- The hierarchy is a **gold-white core, then an orange body, then a crimson torn rim**, wrapped in **black smoke
  billows**. The black smoke is what makes the fire look hot. It's the dark anchor, and it's matter, not an
  outline.
- Afterwards, **molten embers lie pooled on the ground** and keep glowing for a while. Smoke drifts and the embers
  cool. That is our calling card.
- A comet or meteor is a **fire mass around a hard core, with rocks in it and a long straight streak tail**.
- **Molten cracks** are thick, branching, irregular glowing lines. The thick trunk makes them read as fire, and
  thin ones read as lightning.

**Dragons (roblox dragon transformation / rework showcases)**
- The dark-bodied dragons with **glowing lava seams and red-lit wing membranes** read best. The dark body is
  a silhouette against any background, and the seams tie it to the fire VFX.
- Transformations are a **fire wash plus a dark mass** hiding the swap, then a burst. The good ones never show
  the model popping in, because the swap happens behind the densest frame.
- A wide wingspan is the silhouette. A flying dragon reads from its **wing shape**, so the wings have to flap with
  a real fold (downstroke spread, upstroke folded). A rigid plank doesn't read.
- Claw moves in these games use **dark crescents with a hot molten edge**: a charcoal body that burns orange at
  the edge. That suits the obsidian dragon, so our rakes burn hot and their trailing side cools to char.

**Breath (anime breath, Roblox and Unreal breath tests)**
- A breath that reads as a torrent has **volume rolling along it**: billow lobes travelling down the stream, an
  ember spray all around it, dark red outer lobes and a hot inner line. It also **splashes at the ground contact
  point** and leaves a scorch. The stylised version is a tapered tongue cone with a pointed head and a ragged tail.
  A clean cylinder reads as a laser. That's the failure mode we have to avoid.
- Anime breaths start with **one hot line, then a spray of sparks and a ground scorch**. The flash is 1-2
  frames, then colour.

**Tornado (anime fire tornado)**: **spiral bands** wrapping a column, a white-hot core and a darker outer skin,
with the top flaring out. It's banded, not a smooth cone.

**Rules I'm taking from this**
1. Fire layers: thin white-gold core (LightEmission 1), gold-orange body (low LE, covers the sand), crimson rim
   (LE about 0.2, the saturation anchor), translucent orange halo. Fire cools from white-gold to orange, crimson,
   then charcoal. The last step goes alpha-blended, so cooled fire turns into dark char instead of fading to
   nothing.
2. Every big fire shape gets **black smoke** as its dark anchor. That's billowing matter around the fire, never an
   outline.
3. Crescents and tongues tear off along the motion. There are no round fire blobs.
4. The world dims warm-dark (amber tint, lower brightness, more contrast, saturation untouched) for hybrid moves.
   It dims harder for the full form, and stays dim for as long as the dragon exists.

---

## 2. Visual language

**The dragon (original design):** a crimson-and-gold flame dragon with obsidian-black scales. Glowing ember seams
run between the scale plates (molten-orange cracks, brightest on the chest, throat and wing arms). It has swept-back
gold horns (two main horns plus a crown of smaller ones), and a lean, long-necked western build: four legs, a long
tail ending in a flat ember-tipped blade, and big bat-style wings with three fingers. The wing membranes are
crimson, lit from inside like embers, brighter near the bones. Gold eyes. It isn't an azure eastern serpent-dragon,
and it isn't any existing game's or anime's dragon.

**Matter**
| matter | role | sheet |
|---|---|---|
| billowing flame | bodies, impacts, cocoon, breath head | **new** `flame_billow` (layered, 4x4): lobes bloom, roll up, tear into tongues, burn down to char |
| flame tongues | burning ground, pillars, fire on claws/wings | **new** `flame_tongue` (layered, 4x4): one torn tongue licks up and tears off the top |
| flame torrent strips | breath beams, trails, the tornado | **new** `flame_strip_1..4` (layered, tileable along U): rolling lobes and tongues, scrolls seamlessly |
| claw rake | Talon Rend signature | **new** `claw_rake` (layered, 4x4): three parallel burning crescents draw on with a hot leading edge, tongues tear off, the tail cools to char |
| fire crescent | Wing Buffet wall, Tail Cyclone sweep | **new** `fire_crescent` (layered, 4x4): one thick crescent with a torn outer edge |
| fire ring | Sky Drop ring of fire, Firestorm release | **new** `fire_ring` (layered, 4x4, flat): ring wave with a hot leading edge, tongues standing up off it, breaking up |
| fire impact | hits | **new** `fire_impact` (layered, 4x4): star pinch, then a gold burst, then a crimson torn ring, then char flakes |
| molten cracks | calling card (slams) | **new** `molten_crack` (layered, 4x4, flat): thick branching cracks spread, glow white-gold, cool to crimson then charcoal |
| claw gouges | calling card (claws) | **new** `claw_gouge` (layered, 4x4, flat): three scorched gouges glow and cool |
| heat ring | Dragon Roar | **new** `heat_ring` (layered, 4x4): wavering ring, thin hot edge, inner shimmer bands |
| black smoke | dark anchor | re-tint `smoke_cel_v3` charcoal `#2a2226` (3 tone bands) |
| embers, molten rocks | small and mass | reuse `embers` and `lava_drops` (shaded) |
| generic sheets | shockwave, spark burst, flare, streaks, dust ring | re-tint `shockwave_v3`, `spark_burst_v3`, `flare_v3`, `spark_streak`, `smoke_cel_v3` (warm sand dust) |

All sheets are greyscale. Colour comes from the emitters.

**Palette and colour script**
`WHITE_GOLD #fff4c8` -> `GOLD #ffc23a` -> `ORANGE #ff7a1a` -> `CRIMSON #d4202a` -> `EMBER_RED #8a1418` ->
`CHAR #2a2226`. Black smoke `#2a2226`. Dragon gold `#e8b040`.

| layer | role | LightEmission | hot colour | cools to |
|---|---|---|---|---|
| glow | soft halo | 0.75, about 70% transparent | orange | crimson |
| rim | saturated outer body | **0.2** | crimson | ember red, then char (LE drops to 0 so it reads as char) |
| mid | body | 0.4 | gold | orange, then crimson |
| core | hot line | 1 | white-gold | gold, then orange |

**Calling card:** marks left in the sand that glow and cool, with embers drifting off them. Claw moves leave
**claw gouges** and slams leave **molten cracks**. Both start white-gold, cool through orange and crimson, and
end as charcoal scorch that fades last. Small flames lick along the crack lines while they're hot.

**Dark anchor:** black billowing smoke on every big fire shape, plus scorch on the ground.

**Grade:** hybrid moves get a warm dim (brightness -0.1, contrast +0.12, tint `#ffe2c8`). The full form gets a
deep warm dim (brightness -0.2, contrast +0.18, tint `#ffc9a8`) that holds while the dragon exists. Saturation
stays at 0 because desaturating killed the colour on thunder.

---

## 3. The dragon model and rig (the hard part)

**Pipeline (each step shown for approval)**
1. **Concept sheet** (Figma image generation, one image, maybe one retry). Side view with wings spread and legs
   extended, top view with wings fully spread, and a front view with the jaw open. A T-pose-like spread gives Meshy
   clean wing geometry to weight.
2. **Meshy multi-image-to-3D** from the cropped views. **Estimate: 30 credits** (the serpent's job cost 30). Budget
   cap: 60 if one retry is needed. I'll check the balance first and report the spend.
3. **Blender rig** (`scripts/rig_dragon.py`, based on `rig_serpent.py`): orient the head toward -Z, scale to about
   22 studs nose to tail with a 26-stud span, decimate to about 10k tris, cut the mouth on the lip line and add
   a palate and fangs (the serpent's trick).
   - **Spine chain** `spine_00` (head) .. `spine_15` (tail tip): the neck, body and tail. This drives
     path-follow.
   - `jaw` (child of `spine_00`).
   - **Wings, per side:** `wingL_0` (shoulder, the flap), `wingL_1` (elbow, the fold), `wingL_2` (wrist/fingers,
     the membrane tip). These are children of the chest spine bone. Weights are smooth across the span, and the
     membrane is weighted by distance to the arm bones so it folds like a fan.
   - **Legs:** `legFL_0/1`, `legFR_0/1`, `legBL_0/1`, `legBR_0/1` (thigh and shin). They tuck up in flight.
   - Hybrid pieces are **cut from the same model** (zero extra credits, one visual language). The horns are a
     rigid mesh. The claws are a rigid gauntlet mesh per hand. The half-wings are the wing at 0.45x with its own 3
     bones. The tail is the last 40% of the tail at 0.5x with a 5-bone chain. The jaw mask (for Ember Breath) is
     the head front with the jaw bone.
4. **Rig layer v2** (previewer `lab/page/vfx.js` and Luau `templates/ReplicatedStorage/AnimeVFX/init.lua`)
   - `follow: "path"` (current behaviour) or `follow: "rigid"`. Rigid means the skeleton keeps its rest shape and
     the root rides `path`/`move` with `yaw`/`pitch`/`roll` keys. Hovering, roaring and diving need this, because
     path-follow collapses the body when the head stops moving.
   - **Generic per-bone tracks** layered on top of either mode: `boneTracks: {"wingL_0": {"rot": [[t, [x,y,z],
     ease], ...], "loop": 0.6}}`. These are local euler degrees added to the follow pose, with `t` in seconds from
     `t0`. An optional `loop` repeats the cycle (wing flaps), and `mirror: "wingR_"` copies a track to the other
     side with Y and Z negated.
   - **Bone-riding attachments**: any emitter, trail or light can set `bone: {rig: "<layer id>", name: "spine_00",
     offset: [..]}`. That's how breath leaves the jaw, embers drip off the wings and flames ride the comet's head.
   - **Avatar attachments** (`attach` layer): a model or mesh parented to the previewer avatar's `head`, `upper`,
     `armR`, `armL` or `root`, following its pose, with its own bone tracks. In Luau it's cloned from
     `AnimeVFX.Models` and welded to `Head` / `UpperTorso` / `RightHand` / `LeftHand` / `LowerTorso`, with bones
     driven by `Bone.Transform`.
   - Luau mirrors all of this (`Bone.Transform` for tracks, `Bone.WorldCFrame` for path-follow, and the root
     CFrame for rigid). It gets parse-checked with luaparse. It hasn't been run in Studio, and I'll keep saying so.
5. **Validation render:** a looping flap cycle (downstroke spreads and pushes, upstroke folds the elbow and
   wrist) and a dive (climb, wings fold, then a dive), shown to you before any move uses the rig.

**Flap cycle (0.6 s loop):** `wing_0` goes from +35° up to -40° down (down-beat ease-in, the power stroke).
`wing_1` folds 55° on the up-beat and opens on the down-beat, a quarter cycle late (overlap and follow-through).
`wing_2` lags `wing_1` by a further eighth. The body bobs 0.4 studs counter to the beat, and the tail lags the body.

---

## 4. Moveset

Timing defaults: hit-stops 0.04-0.08 for small hits and 0.12-0.18 for big ones, starting about 1 frame after the
strike. One flash per beat (1-2 frames). Only the four biggest hits (Sky Drop, Transform, Inferno Torrent, Comet
Dive) get an inverted or mono impact frame. Every move uses all five rules.

### Hybrid form (horns, clawed arms, half-wings, tail on the avatar)
The hybrid pieces are on for every hybrid move: horns on the head, claw gauntlets on both hands, half-wings on the
upper back (idle: a slow half-flap every 1.2 s), and the tail at the hips (idle sway). Embers drip off the claws
and wing edges.

#### Z: Talon Rend (1.6 s): triple claw combo
- **Mechanic:** three melee rakes at one target (R, L, then a big overhead finisher).
- **Signature:** three parallel burning crescents (`claw_rake`). Each rake hangs in the air at its own angle, so
  after the third they form a burning **triangle of slashes**. Their trailing sides cool to char while the
  **gouges** of the finisher appear in the sand under the target.
- **Beats:** 0.00-0.18 wind-up (lean back, right arm drawn back, claws ignite with tongues, embers pulled in) /
  0.18 rake 1 diagonal down-right, **hit-stop 0.05** / 0.38 rake 2 mirrored up-left, **0.05** / 0.50-0.62 both
  arms raised, half-wings flare / 0.62 finisher overhead downward (the biggest rake, 9 studs), **0.12**, target
  knocked back and squashed, gouges ignite / 0.8-1.6 rakes cool to char and flake into embers, gouges cool, smoke
  drifts.
- **BIG:** the finisher rake plus the ground gouges. **Medium:** `fire_impact` on the target per rake, one flare
  on the finisher. **Small:** ember sparks and short streaks along each rake's direction.
- **Mass:** black smoke puffs off the target, dust kick on the finisher, the gouges.
- **Camera:** close three-quarter view, then a push in on the finisher.

#### X: Wing Buffet (1.5 s): the wings snap open
- **Mechanic:** a short-range forward shove (knockback, no big damage).
- **Signature:** a **wall of flame-wind**. A broad, flat, curved flame sheet (14 studs wide, 5 tall, made from
  `fire_crescent` laid horizontally plus scrolling `flame_strip`) rolls forward along the ground with **gust
  lines**: long horizontal streaks with embers riding them. It's the only move whose shape is a wide wall moving
  forward.
- **Beats:** 0.00-0.30 wings wrap forward around the body, crouch, embers sucked in / 0.30 SNAP: wings fling open
  and forward (bone tracks), a 1-frame flash at the chest / 0.30-0.85 the wall travels 0 to 14 studs ahead and
  slows (ease-out). Two targets slide back with it, **hit-stop 0.06** on contact / 0.55 a smaller second beat
  pushes a thinner second wall / 0.85-1.5 the wall tears into tongues and dies, a wedge of sand dust is blown
  forward, and embers settle.
- **BIG:** the wall. **Medium:** a sand-dust wedge, the chest flash. **Small:** gust streaks and embers.
- **Mass:** a wedge of dust blown flat along the ground, black smoke shoved ahead of the wall.
- **Camera:** behind the caster and low, so the wall rolls away from camera toward the targets.

#### C: Sky Drop (2.2 s): leap and claw dive
- **Mechanic:** a gap-closer and AoE slam.
- **Signature:** a **ring of standing flames** around a crater with **radial molten cracks** (the slam calling
  card).
- **Beats:** 0.00-0.15 crouch (squash) / 0.15 leap with 2 wing beats, rising to 16 studs and 10 forward, fire
  trail from the feet / 0.75-0.9 apex hang: wings spread wide, the body flips claws-down, claws ignite /
  0.90-1.05 dive (stretch, straight streaks, falling fire trail) / 1.05 **IMPACT, hit-stop 0.15, one mono frame**:
  crater plus molten cracks, a `fire_ring` races out to 9 studs, and flame tongues stand up all around the ring
  and burn for 1 s / 1.05-2.2 the player rises from the crouch, the ring burns down, the cracks cool, black smoke
  rolls up.
- **BIG:** the ring of fire. **Medium:** shockwave, impact flare, dust ring. **Small:** streaks, sparks, embers.
- **Mass:** crater slabs, flung rocks, a dust ring hugging the ground, a black smoke column.
- **Camera:** wide and low for the leap, tilting up to follow, then a push in and a shake on the impact.

#### V: Tail Cyclone (1.8 s): 360 tail sweep
- **Mechanic:** a close AoE around the caster, with a delayed eruption.
- **Signature:** the sweep **draws a burning ring** on the ground. A beat later the ring **erupts in a crown of 8
  flame pillars in sequence** around the circle.
- **Beats:** 0.00-0.20 wind-up twist, tail coiled back / 0.20-0.60 full 360 spin, tail extended (bone track). The
  tail tip draws a flat flame trail on the ground at radius 6 and the circle closes / 0.60-0.75 the ring
  smoulders and pulses (anticipation for the eruption) / 0.75-1.05 8 pillars erupt one after another, 0.04 s
  apart, going around. Each is a column of tongues with a billow at the top. Targets on the ring are launched
  up, **hit-stop 0.07** on the pillar that catches one / 1.05-1.8 pillars collapse into black smoke, embers rain.
- **BIG:** the pillar crown. **Medium:** the burning ring, billows topping the pillars. **Small:** embers, sparks.
- **Mass:** a dust ring from the spin, black smoke from the pillar tops, small rocks.
- **Camera:** high three-quarter view so the full circle reads.

#### B: Ember Breath (1.5 s): short cone breath
- **Mechanic:** a short-range cone (10 studs), sweeping 50° left to right.
- **Signature:** a **fan-shaped scorched wedge** burned into the sand, studded with small licking flames. It's
  short and wide, the opposite of the full form's long line.
- **Beats:** 0.00-0.30 inhale: head rears back, the jaw mask forms over the face (scales in from the horns), the
  throat glows, embers sucked into the mouth / 0.30-1.10 breath: the jaw opens (bone track). A cone of
  `flame_billow` lobes and tongues spills from the jaw bone (velocity-parallel, 22° spread), with the head
  sweeping 50°. Scorch decals and small flames are laid along the sweep arc, **hit-stop 0.04** on the first
  contact per target / 1.10-1.50 the jaw snaps shut, smoke curls from the nostrils, the wedge smoulders and cools.
- **BIG:** the cone and the scorched wedge. **Medium:** billows at the cone's mouth, impact flames on targets.
  **Small:** an ember spray.
- **Mass:** black smoke riding the top of the cone, scorch.
- **Camera:** side three-quarter view so the fan shape reads on the ground.

#### F: Transform (2.8 s): flame cocoon to full dragon
- **Signature:** a **flame cocoon** that swells, then **bursts** with the dragon's wings snapping open and a roar
  shockwave.
- **Beats:** 0.00-0.40 the player crouches, a circle of tongues rises from the sand, embers spiral inward /
  0.40-1.20 the tongues wrap up into a spinning closed cocoon (an egg of tongues, billows and scrolling
  `flame_strip` bands), 5 studs growing to 12. **The silhouette swells**: the avatar scales 1 to 2.2 and chars dark
  inside the fire / 1.00-1.45 **hidden swap**: during the densest cocoon frames the avatar fades out while the
  dragon rig fades in, scaling 0.5 to 1 with wings folded. Neither is ever crisp and visible at the same time, so
  nothing pops / 1.45 the cocoon pinches inward (anticipation) / 1.50 **BURST, hit-stop 0.16, one inverted
  frame**: the wings snap open (bone tracks), the cocoon tears outward as a `flame_billow` ring plus a shockwave,
  the jaw opens on a roar with 2 heat rings, a dust ring and black smoke wall roll outward, rocks fling / 1.5-2.8
  roar holds then closes, embers rain, ground flames burn down, the dragon lifts into a hover (flap cycle). The
  world dims to the full-form grade and stays dim.
- **BIG:** the cocoon, then the burst. **Medium:** shockwave, heat rings, dust ring. **Small:** embers, streaks.
- **Mass:** a black smoke wall, rocks, scorch, molten cracks under the cocoon.
- **Camera:** close and low on the cocoon, pulling back on the burst to fit the full wingspan.

### Full form (you are the rigged dragon: flying, flapping, jaw, tail)

#### Z: Inferno Torrent (2.6 s): charged breath beam
- **Mechanic:** a long beam that sweeps a line on the ground (about 25 studs long).
- **Signature:** a **line of fire left behind the sweep**: a scorched stripe with flames erupting along it in
  order, like a fuse.
- **Torrent, not laser:** a `vbeam` of 3 crossed `flame_strip` plane sets (crimson rim, gold body, a thin
  white-gold core twisting the other way), a **stream of billow lobes travelling down the beam**
  (velocity-parallel emitter on the jaw bone, speed 60), an ember spray around it, black smoke riding its top,
  and a **splash** at the ground contact (billows and tongues fanning out, sand dust).
- **Beats:** 0.00-0.60 hover. The head rears back, chest and throat seams brighten (embers riding the chest bone),
  flame swirls gather into the jaw, smoke trickles from the nostrils / 0.60 release: a 1-frame flash at the jaw,
  the body recoils back and the wings flare / 0.60-1.80 the beam's contact point sweeps the line, the scorch
  stripe is laid behind it, and pillars erupt along it 0.08 s behind the contact / 0.95 it crosses the main
  target: **hit-stop 0.12, one mono frame** / 1.80-2.6 the beam thins and cuts, the jaw closes, the fire line
  burns down to embers and the scorch cools.
- **BIG:** beam and fire line. **Medium:** contact splash, jaw flash. **Small:** embers, sparks.
- **Mass:** black smoke, sand dust, scorch stripe.
- **Camera:** side-on and elevated, so the dragon, beam and whole line are in one frame.

#### X: Comet Dive (2.6 s): burning comet
- **Mechanic:** a high-damage AoE dive.
- **Signature:** the **comet**, a fire mass enveloping the folded dragon with a long straight streak tail, then a
  **molten rock rain** after impact.
- **Beats:** 0.00-0.60 climb up and back with 2 hard wing beats / 0.60-0.80 apex: the wings fold tight (bone
  tracks), the body rolls nose-down (anticipation hang) / 0.80-1.25 dive: a `flame_billow` mass on the head bone
  stretches back (squash and stretch), straight streaks and smoke trail behind / 1.25 **IMPACT, hit-stop 0.18,
  one mono frame**: a big crater (radius 12), huge molten cracks, shockwave, a billow column with black smoke
  mushrooming, rocks / 1.30-2.40 **molten rock rain**: `lava_drops` and rocks flung up on arcs, each landing
  with a small ember splash and a glowing spot / 1.60 the dragon bursts up out of the smoke with one wing beat
  and hovers.
- **BIG:** the comet, then the crater blast. **Medium:** shockwave, flare, smoke mushroom. **Small:** streaks,
  embers, the rock rain.
- **Camera:** wide and low near the impact point, so the comet comes in from upper screen with a long tail.

#### C: Firestorm Wings (3.0 s): fire tornado
- **Mechanic:** sustained AoE around the dragon that pulls enemies in and lifts them.
- **Signature:** a **banded fire tornado column** around the hovering dragon (spiral bands, a white-hot inner
  edge, a crimson outer skin, flaring at the top).
- **Beats:** 0.00-0.40 the dragon rises to a hover, wings go wide (anticipation) / 0.40-2.40 hard wing beats
  every 0.5 s. **Each beat pumps the tornado**: the band speed surges, a dust ring is sucked inward, flame tongues
  orbit faster. The tornado is spiral shells (`swirl` mesh with scrolling `flame_strip`, two counter-rotating)
  plus orbiting tongues and ember spirals. Enemies are lifted and spun, with **hit-stops of 0.04** on ticks at
  1.0, 1.5 and 2.0 / 2.40 a final big beat: the tornado **bursts outward** as a `fire_ring`, shockwave and
  billows, **hit-stop 0.10**, enemies flung / 2.4-3.0 embers fall, smoke drifts.
- **BIG:** the tornado. **Medium:** the burst ring, billows. **Small:** orbiting embers, sparks.
- **Mass:** debris orbiting in the column, dust drawn in at the base, black smoke at the top.
- **Camera:** wide, low and looking up the column.

#### V: Dragon Roar (2.0 s): stun roar
- **Mechanic:** a stun with a push-back. No fire projectile.
- **Signature:** **concentric heat and sound rings** pulsing from the jaw (`heat_ring`, camera-facing), plus a
  **ground ripple** that travels outward through the sand as a dust wave. Enemies stagger and a dazed ember swirl
  circles their heads.
- **Beats:** 0.00-0.40 the head rears up and back, wings rise, the jaw opens slowly, embers pulled in, the camera
  drifts in / 0.40 ROAR: the jaw goes fully open and the head thrusts forward. Ring 1, **hit-stop 0.12**, ground ripple,
  heavy shake (no inverted frame: the rings are the hit) / 0.62 and 0.84 rings 2 and 3 (smaller, fainter) / 0.4-1.2 enemies
  pushed back, stun swirls / 1.2-2.0 the jaw closes, smoke rolls out of the mouth.
- **BIG:** the ring burst. **Medium:** ground ripple, dust ring. **Small:** embers, the stun swirls.
- **Mass:** a sand wave, dust ring, loose debris hopping.
- **Camera:** in front of the dragon's head, low, with the rings coming at camera.

#### B: Ash Rain (3.2 s): fireball barrage from above
- **Mechanic:** zone denial. The dragon circles overhead and rains fireballs in a pattern.
- **Signature:** a **spiral of small craters** burned into the ground, with ash drifting over the zone.
- **Beats:** 0.00-0.50 climb into a circle (path-follow mode, radius 12, altitude 18) / 0.50-2.40 a fireball
  drops from the jaw every 0.19 s (10 total). Each one arcs down along a spiral pattern (small billow plus trail)
  and lands with a mini crater, a mini molten crack, `fire_impact`, embers and a black puff. **Hit-stop 0.04** on
  the ones that hit targets. Grey ash flakes fall over the zone the whole time / 2.40-3.2 the dragon pulls out of
  the circle, the craters smoulder and cool one by one in drop order.
- **BIG:** the circling dragon plus the spiral pattern. **Medium:** each impact. **Small:** ash, embers.
- **Mass:** craters, smoke puffs, ash.
- **Camera:** high and wide over the zone.

#### F: Revert (1.6 s): back to the player
- **Signature:** the dragon **collapses into flame** and the player drops out of it.
- **Beats:** 0.00-0.35 the dragon lands low and the wings wrap around the body (bone tracks) / 0.35-0.80 the body
  breaks into flame: the rig tint heats to orange and fades, tongues and billows burst from the bone positions
  (bone-riding emitters), and everything collapses into a shrinking flame pillar / 0.80 the player drops out at
  scale 1 and lands with a squash, with a small ember ring / 0.8-1.6 embers settle on the sand and cool, and the
  grade ramps back to normal. No hit-stop (nothing is hit).
- **BIG:** the collapsing flame. **Medium:** ember ring. **Small:** settling embers.
- **Mass:** smoke lifting off, scorch where the dragon stood.

---

## 5. Order of work (each step waits for approval)
1. This doc (now).
2. Concept sheet (Figma image gen).
3. Meshy model (about 30 credits), Blender rig with wings, rig layer v2 (previewer and Luau), then the flap cycle
   and dive render.
4. Fire matter: paint the new sheets, then a contact sheet and tinted previews.
5. Hybrid Z, X, C, V, B, F, one at a time.
6. Full form Z, X, C, V, B, F, one at a time.
7. Second pass on all 12.
8. `python3 scripts/export_luau.py --effects lab/dragon/moves` and the upload manifest (textures, meshes, rig
   models). No upload.

## 6. Open questions for you
- **Scale:** a 22-stud-long dragon with a 26-stud wingspan (a player is about 5 studs). Bigger reads more epic but
  fills the frame in the arena. Is that OK?
- **Hybrid tail:** a skinned 5-bone tail (it sways and sweeps for real), or a cheaper rigid tail with rotation
  keys only? I'm planning the skinned one.
- **Inverted frames:** only Sky Drop, Transform, Inferno Torrent and Comet Dive get one. The Roar relies on its
  rings and shake instead. Should the Roar get one too, swapped in for Inferno Torrent?
