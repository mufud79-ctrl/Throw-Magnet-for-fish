# Harsh review checklist

Compare **reference vs ours** with `scripts/compare.py` in a matching camera view, then also look at the front and side
previews. Go through every line and write down each difference, worst first. Fix the worst three, rebuild, compare again.
Stop only when a fresh pass finds nothing at the silhouette, proportion or face level.

## A. Silhouette & proportion (fix these first)
- [ ] Squint: does the overall mass shape match (mound vs table, upright vs horizontal)?
- [ ] Highest point in the right place (head peak vs back hump)? Does any box corner poke out of the outline? (Use `hexa`.)
- [ ] Head size vs body: compare head height / total height and head width / total width.
- [ ] Leg length and thickness, and how much air shows under the belly.
- [ ] Length/height ratio of the whole animal. Neck length. Tail length and angle.
- [ ] Signature parts present and big enough (muzzle, horns, wings, crest, tail gems)?
- [ ] Front view: wings, ears and fins visible, not edge-on? Side view: nothing hidden or floating?

## B. Face
- [ ] Eye size, spacing and position on the head; do they protrude?
- [ ] Pupil size and offset (look direction). Is the pupil square?
- [ ] Brow thickness, tilt direction (angry = inner end DOWN) and gap to the eye (should touch).
- [ ] Teeth: blades facing sideways (not needles), count, size, spacing, fangs.
- [ ] Mouth gape angle, mouth/tongue colours, jaw colour (white jaws on reptiles).

## C. Colour & surface
- [ ] Hue, saturation and value vs the reference (preview lighting can wash out light colours; judge mid-tones).
- [ ] Second colour areas (belly, throat, muzzle) in the right place and size.
- [ ] Studs present on the right parts, the right density, subtle enough? Missing on faceted animals?
- [ ] Gradients dominated by the tip colour?
- [ ] Mutation preview (if the reference is a mutation): saturated, eyes/teeth untouched.

## D. Rig & animation (previews/<Name>_anim.png: rows = Idle, Walk, Fly)
- [ ] Every part follows a bone: nothing floats or stays behind when legs/head/wings move.
- [ ] Walk: diagonal leg pairs (quads) or alternating legs + counter-swinging arms (bipeds); feet don't sink far below ground.
- [ ] Fly (winged): wings flap symmetrically, body lifts, legs tuck. Flightless birds have no Fly clip.
- [ ] Idle: head looks around, body breathes, tail wags; unanimated bones sit at rest (no pose left over from another clip).

## E. Export sanity
- [ ] `TRIS` line under 20k per mesh. Size in studs plausible.
- [ ] Facing: the animal looks toward Roblox -Z (the kit does this; don't rotate the build).

## Known pitfalls (already hit; check for them)
| Symptom | Cause | Fix |
|---|---|---|
| Brows look sad | tilt sign | `angry > 0` lowers the inner end (kit handles the mirroring) |
| Eyes invisible | sunk behind the brow ridge or muzzle, or too small | put them on a vertical face plate, `depth` 0.2+, size up to 1.5 studs |
| Back hump taller than the head | a rotated box's corner rises | define the back with `hexa` corners |
| Rainbow pastel | ramp colours in sRGB | (fixed in the renderer) |
| Teeth look like needles | spike blade axis | `flat=0.3` (blade is wide along X) |
| Wings are sticks from the front | feathers fanned in the XZ plane | spread `d` and the feather plane sideways, swept back about 35° |
| Feathers look muddy orange | 2-stop gradient | 3 stops, tip colour dominant |
| Pale colours look white | preview over-exposure | judge mid-tones; keep belly colours fairly saturated |
| Black bar on the image edge | outline wrap | (fixed: padded dilation) |
| Black square holes on small animals | bevel wider than a stud cell inverted faces | (fixed: grid lines inside the chamfer zone are dropped) |
| Idle shows legs mid-stride | unkeyed bones kept the previous clip's pose | (fixed: every clip keys every bone) |
| Black squares where legs meet the body | leg face coplanar with the body side (Cycles black, Roblox z-fight) | inset parts a little; never let two faces share a plane |
| Spots stick out as slabs near the rump | patches placed over the tapered/chamfered ends | keep patterns on the flat middle (archetype `pattern` does) |
