# Hero builds: the Chimera method (user-approved: "THAT LOOKS SO GOOD!!")

The user's quality bar for **every animal from now on** is the Chimera (`examples/chimera.py`). Archetype one-liners
(`tffa_zoo.py` specs) produced "dog with wings", "baby squid", "box on a stick" heads. What worked was a dedicated,
reference-driven script per animal. Use this method for every animal in every remaining zone.

## 1. Get and analyse a reference (before writing any code)
- Use the user's image if given. Otherwise pick the animal's most iconic, dramatic depiction (a painting/concept art
  pose, not a cute toy) and describe it in writing first.
- Write the analysis as a numbered list, **most important first**, and keep it in the script's docstring:
  1. **Pose / silhouette**: what is the highest point? Where does the head sit relative to the shoulders? Leg stance
     (crouched, wide, reaching)? Line of the back? (Chimera: stalking crouch, shoulders highest, head BELOW the shoulder line.)
  2. **Head**: shape, expression (snarl / roar / calm), eye size and glow, brows, mouth state.
  3. **Signature parts** that make the creature recognisable: horns, extra heads, tail type, wings, mane. Note their size
     relative to the body (Chimera horns are as tall as the body) and their curve (C-curve, swept back, spiralled).
  4. **Colours**: base, secondary (mane/belly), accents (red horn tips, glowing eyes), max 3 hues + accents.
  5. **Surface details**: scars, scales, rings on horns, claws, belly plates.
- Translate each point to TFFA blocks (style_guide.md): chunky chamfered parts, studs on big faces, block eyes + brows.

## 2. Write a custom script `examples/<animal>.py`
- Start from the closest finished example (`chimera.py` for beasts/hybrids, `dragon.py` for winged reptiles, `trex.py`
  for theropods, `gorilla.py` for apes, `cow.py` for plain quadrupeds). Build directly with kit primitives - no archetype.
- Body as 3+ stacked boxes (chest / waist / hips) so the back line can slope; extra boxes for haunches and shoulder
  muscle; a separate darker `Back` strip. Never one box for the body.
- Use `m.frame(pivot, scale, rot, move)` to place, size and tilt sub-assemblies (a goat head, an open jaw, a snake mouth)
  instead of recomputing coordinates; this is also how you apply the user's "move it / lower it / bigger" notes in one line.
- Rig with the standard bone names (`Body`, `Neck`, `Head`, `Jaw`, `Leg_FL/FR/BL/BR`, `Tail1..n`, `Tent<k>_<j>`, `Wing_L/R`).
  Extra heads ride the `Neck` bone; snake tails are `m.chain(..., bones="Tail")` with belly/back detail inside each `Tail<i>` bone.
- Register it in `tools/blender/tffa_zoo.py` as `("<Name>", EX, "<script>")`. Build a single animal with
  `TFFA_ANIM_PREVIEW=0 /tmp/bpyenv/bin/python .claude/skills/tffa-animal-models/examples/<script>.py <out_dir>`.

## 3. Techniques that sold the Chimera (reuse them)
| Look | How |
|---|---|
| Menacing stance | shoulders highest; head centre below shoulder top; front paws forward + wide (`seg` forearm angled out), hind legs coiled (thigh `rot=Ry(0.4)`) |
| Shaggy mane / fur cape | thick `Mantle` box over the shoulders + `spike(..., flat=0.55)` tufts **swept backward** (tip = base + (-1.2, y*1.15, +0.5)); side `Fringe` boxes with downward tufts |
| Wild face ruff | ring of spikes round the face, each pointing back + outward (`b + (-1.0, y*L, z*L)`), alternating two tones |
| Snarl | open mouth box (MOUTH), top teeth row + long fangs, jaw on a `Jaw` bone opened with `frame(rot=Ry(0.45))`, tongue, nose wrinkles, squinted eyes (h 0.4) with steep brows (angry 0.5) |
| Glowing eyes | `eyes(white=ORANGE, glow_white=True)` + `done(glow_color=...)`; small glowing eye boxes for secondary heads |
| Huge ringed horns | 4 `seg` sections along a C-curve, a slightly wider dark `HornRing` seg at each section's middle, colour shift near the tip (dark -> red) and a `spike` tip; thick at the base (0.44 -> 0.16) |
| Scaled snake tail | 8-point `chain` (thick 0.85 -> 0.5) routed round the flank to the front, head raised; pale belly boxes underneath + dark diamond boxes (`rot=Rz(0.785)`) on top; open jaw via `frame(rot=Ry(0.55))`, fangs, slit pupils |
| Claws | 3-4 dark flat `spike`s per paw pointing forward-down; reddish/darker lower legs |
| Scars | thin dark boxes (`studs=False`) on the shoulder at varied angles |

## 4. Review loop
- Render `views=[("hero",40,12,45), ("front",0,8,45), ("side",90,4,45), ("ref", az, el, 45)]` with "ref" matching the reference camera.
- Put the 4 views in one 2x2 sheet (`<Name>_review.png`) and compare against the analysis list, worst first.
- When heads are the problem, **do head studies**: 4 variations of the head alone on a neck stub
  (`tools/blender/tffa_head_studies.py`), show the user, build from the one they pick. Picked heads become head kits
  (`HEAD_KITS` in tffa_archetypes.py: `lion_sunburst`, `horse_wedge`).
- When a whole animal misses ("looks like a normal bunny", "looks bad"), build **4 full-body variations with clearly
  different concepts** (`tools/blender/tffa_space_variants.py` is the template: one builder function per variant, shared
  head/body helpers, one sheet per animal with hero/front/side rows). The concept must change the SILHOUETTE (a planetary
  ring round the waist, a moon body, a comet tail, antennae + crystals), not just add decals. User picks, then refine.
  Picks so far: MoonBunny = Saturn (ringed galaxy bunny), SpaceCat = Alien (third eye, antennae, crystals, orbs).
- When the user asks for a full rework, archive the old model to `models/CannonTame/Animals/_Archive/<Name>_v1/` and keep
  the old spec as a comment in the roster; never silently overwrite a version the user may want back.
- Show the user the review sheet after each round and apply their notes literally ("over the centre", "lower it").
