# Thunder fruit base moves: working notes (branch claude/thunder-moves-950cm0)

Sub-session of the thunder fruit work. Scope: the 7 base moves as VFX (Volt Lance Z, Thunderclap X, Judgment
Pillar C, Flash Step V, Thunder Serpent B, Static Field N, Plasma Bomb M). The god model, drums, cutscene and
god-mode moves stay on `claude/ecstatic-mayer-950cm0`; THUNDER_HANDOFF.md is not edited here.

## Layout
- `lab/thunder/moves/*.json`  hand-authored move specs (one per move, no effects.py archetypes)
- `lab/thunder/tests/*.json`  test specs for new layer types
- `lab/thunder/strip.sh`      dense frame strip around a beat: `strip.sh video.mp4 start end out.jpg [cols] [width]`
- `assets/renders/thunder/`   rendered MP4s + frame strips shown to the user
- Render: `node lab/render.mjs lab/thunder/moves/<move>.json --out lab/out/thunder`
- Export (after all 7 approved): `python3 scripts/export_luau.py --effects lab/thunder/moves`
  (the default `lab/effects` is the rejected 100-move batch: do not export it with these)

## Step 2: new layer types (polish pass 2, waiting for approval)
- `trail`: real Roblox Trail on two attachments riding `path` / `move` / `wave`. Ages on real time like Roblox,
  so a hit-stop holds the head and the tail keeps fading (previewer matches). Texture swapping for strip variants.
- `vbeam`: Neon/ForceField cylinder core + optional sheath + lists of crossed Beam plane sets (taper, twist,
  scroll, swap). Plane width axis in Roblox is an assumption (`PLANE_WIDTH_AXIS` in init.lua): check in Studio.
- `path` (time-keyed polyline) and `wave` (sinusoid on top, amp keys) work for every attached layer.
- Lessons: additive white on sand blooms to a white slab. Keep Neon cores thin (<= 0.2 radius), ForceField
  sheaths dim (brightness ~0.3), and give every ribbon/beam a navy alpha-blended (lightEmission 0) layer.
- Luau parse check: luaparse 0.3.1 after rewriting `x += y` (script in the session scratchpad; recreate with
  `npm i luaparse@0.3.1`). Not run in Studio.

## Polish pass after "looks like poop" (user feedback on the first test renders)
The first tests were thin white noodles: no caster, far camera, no colour script, no flicker/afterglow, no scar,
and the beam was a white slab. Every render shown, tests included, must meet the full bar. Fixes now in `lab/thunder/kit.py`:
- Layer conventions of the approved textures: glow additive blue, **rim alpha-blended indigo (LightEmission 0)**,
  mid cyan LE 0.1, core white LE 0.35. The indigo rim keeps lightning saturated and outlined on sand.
- Colour script over cooling age (white -> cyan -> blue -> indigo), flicker as a transparency sequence
  (solid strike, two-on-one-off, fade), widthScale squash (fat on the strike, thinning as it cools).
- PointLight brightness <= ~8 and range ~10-14: hotter floods the sand with white pools.
- Hit-stop starts one frame (~0.025 s) AFTER the strike so the frozen frame shows the bolt; at exactly T the
  emitters and reach haven't fired yet. vbeam reach for lightning = 1 (instant).
- Angular ribbons: one trail per straight leg (`leg_trails`) so kinks stay sharp (a Trail samples once a frame
  and rounds corners between samples, in Roblox too). Static texture mode, textureLength ~16 so runs read straight.
- Burn scar calling card `scar()`: lichtenberg stack flat on the ground cooling through the colour script over
  a soot scorch that fades last.
- Frame cameras so the whole action is in shot with the caster visible; elevate it when the path zig-zags on the ground.

## Polish pass 3 ("more polish")
- Renders at 1280x720: `node lab/render.mjs ... --hd` (show the user HD; 640x360 looks soft).
- No camera-facing thunder_burst rings (perfect thin circles = vector look). Use `crackle()` (thunder_arc played
  once) for air flashes and `ground_ring()` (thunder_burst laid flat) so the ring becomes a shockwave on the ground.
- RELL impact weight: `dust()` (dust_burst, warm grey #d9d3c6 at brightness 1: white blooms into a glow blob),
  `smoke_burst()` (navy smoke_puff), fling debris.
- Instant strike = neon `bolt` layers hugging the beam (jitter <= 0.6, 14 segments, thin) for 2 frames + one re-strike.
- Neon core cylinder radius <= 0.15 (a fat core reads as a white slab near the camera); glow plane brightness 0.6.
- Caster life: ghost afterimage on dissolve, arcs + static dripping off the body after re-forming.
- Camera: frame the whole action with the caster in shot; small push + FOV punch (about 5 deg) on the hit.
- Grade: storm dim = slight darkening + contrast, keep saturation (desaturating reads drab against RELL).
- Trim dead frames at the end.

## Texture v2: cel lightning from an Enel (anime Goro Goro) reference study
User: "textures need more polish, cutoff edges and poor clarity ... look up Enel". Reference frames came from YouTube's
published thumbnails (i.ytimg.com maxres/hq frames; the fandom wiki refuses automated fetches). Style reference only:
no Enel names or likeness in the moves.
What the reference shows: thin white core in a FLAT saturated cyan body with a hard edge and a tight halo (cel, not soft
bloom); jagged straight runs with fine micro-jags and short hooked barbs that taper to points; bolts bunch into a
crackling bush; charge = white pinpoint star with speed rays; big hits flash the whole frame pale cyan line-art;
ground hits = tall thin white-violet streaks shattering slabs.
Done: new `cel` texture kind in vfx_textures.py (explicit layers, tapered polygon strokes with mitred joins, pointed
tips, draw-in follows the trunk) -> thunder_bolt_v2, thunder_burst_v2, thunder_arc_v2, thunder_strip_v2_1..4.
Kit + showcases switched to v2. Comparison sheets: assets/previews/v2_compare/. User: "Much better" -> v2 textures and the trail/vbeam types approved.
Ideas from the reference still to use in moves: cyan-mono impact frame for the biggest hits (Judgment Pillar),
pinpoint charge star with rays (Plasma Bomb hold), tall white-violet streak + slabs for ground strikes.

## Move 1: Volt Lance (Z) - approved ("Nice")
Spec script `lab/thunder/moves/volt_lance.py` -> `thunder_01_VoltLance.json`; render + strips in assets/renders/thunder/.
Mechanic: hitscan javelin. Signature (no other move uses it): after the 1-frame line strike the shaft SNAPS SHORT
into a compact cel spear impaled through the target (neon spike head out its back), riding the knockback, flickering,
cooling, dissolving tail-to-head, head shattering into sparks. Wind-up: spear crackles into the raised hand and pinches.
Camera: wide side-on for the throw, glides in on the impaled target after the strike.
Lessons: the strike bolt must end before the shaft snaps (else a disjoint white noodle); a lingering full-length line
just reads as a beam, so the signature has to change shape; spear needs width ~2-5 studs to read at game distance.

## Move 2: Thunderclap (X) - approved ("Okay")
`lab/thunder/moves/thunderclap.py` -> `thunder_02_Thunderclap.json`. Mechanic: AoE stun around the caster.
Signature: a geodesic dome cage (25 curved crackling edges = 75 camera-facing Beams) bursts out on the clap,
overshoots 10 studs, edges blink individually, shrinks back as it cools; arcs crawl on the 3 stunned targets.
Wind-up: hands spread overhead with an arc between the palms that tightens as they close. Camera: close on the
wind-up, snaps wide on the clap to reveal the cage.
Runtime upgrades for it: beam `from` keys, `curve` (keys) in Luau via CurveSize Bezier, beam texture swapping.
Perf note: 75 Beams for the cage; on low Quality drop the rim layer (50 Beams).

## Move 3: Judgment Pillar (C) - approved ("That one looked amazing")
`lab/thunder/moves/judgment_pillar.py` -> `thunder_03_JudgmentPillar.json`. Mechanic: placed delayed strike (1.0 s warning).
Telegraph: storm_cloud billows 38 studs up (+ smoke_puff fringe), inner flashes = storm_flash played in 0.13 s behind
the cloud (ZOffset -3) so they rim-light it instead of punching a disc; cloud shadow + a ring of crawling flat ground
arcs mark the zone; world grade darkens; stepped leaders (beams with flickering reach) + ground streamers.
Strike: vbeam column (4-plane cel stack + navy set), 5 braided curved strand beams, giant thunder_bolt_v2 sprite,
ONE inverted impact frame, hit-stop 0.15, crater slabs + fling, giant ground starburst, dust, smoke columns, 2 re-strikes.
Camera: back and up (cloud, column, ring and caster in one frame).

## Fix: burn scars were invisible in every render
scar() used a negative ZOffset on flat ground decals: ZOffset moves a particle along the view ray, so negative pushes
the quad into the ground and the ground hides it (Roblox does the same). Ground decals now sit at y 0.06-0.1 with
ZOffset >= 0. Moves 1-3 re-rendered (only change: their scars now show).

## Move 4: Flash Step (V) - approved ("Yes")
`lab/thunder/moves/flash_step.py` -> `thunder_04_FlashStep.json`. Approved timing (0.08 dissolve, 0.12 s zig-zag, 0.20 re-form).
Signature: 4-leg angular cel ribbon (leg_trails) + a 1-frame silhouette flash at each corner + a dotted chain of burn
scars along the route (start, 3 corners, end) - the route stays written on the ground after the ribbon fades.

## Move 5: Thunder Serpent (B) - concept stage
User: "You might need a rigged model for that too, u can use meshy if needed". Plan (each step shown for approval):
1. concept sheet (Figma image gen, file "Anime VFX source art", gpt-image-2.5-flare): assets/source_art/thunder_serpent/serpent_sheet_v1.png
   (side view straight body, top view, head front with jaw open; original design, not Enel)
2. Meshy multi-image-to-3D (~30 credits, check balance first) -> cleanup ~6k tris
3. Blender rig: 14-bone spine chain + jaw bone
4. new `rig` layer (previewer three.js SkinnedMesh + Luau skinned MeshPart, Bone CFrames driven so the spine follows the path)
5. the move: glowing cel serpent + braided chained lightning ribbons, S-curve swim, coil around the target, burst.
Beat sheet (from the approved design): 0.00 arm sweep / 0.25 serpent born from the hand / 0.25-0.85 swims an S-curve /
0.85 coils around the target and bursts / 1.3 afterglow.
