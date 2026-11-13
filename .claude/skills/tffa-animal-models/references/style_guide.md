# TFFA style guide (measured from the real game shots in `ref_images/`)

## 1. Two looks, chosen by rarity / kind
| | **Studded** (common & natural animals) | **Faceted** (rare, mythic, fantasy, monsters) |
|---|---|---|
| Examples | gorilla, T-Rex, cow, dog, penguin; foods (carrot, banana, burger) | red dragon, phoenix, pumpkin spider |
| Surface | stud texture on every big face | no studs, flat colour |
| Colour | 1 body colour + 1 belly/face colour + black/white features | 2-3 colours plus **gradients** (feathers yellow at the tip, orange at the base) |
| Shapes | chunky boxes and frustums | angular low-poly: tapered segs, spikes, plates, membranes |

Both looks share the geometry language below.

## 2. Geometry language
- **Everything is a chamfered block.** Boxes, frustums (`top=` scale), tapered segments and wedges, each with a flat chamfer of
  12-22% of its smallest side. Use **flat shading** everywhere (faceted, never smooth-shaded blobs). No spheres for body parts.
- **Organic forms come from stacking**: a dome back is a frustum, a crest is a frustum with `shift`, a tail is a stepped
  `chain`, a carrot is stepped segments. Parts overlap generously, so there are no gaps or visible seams at joints.
- **Silhouette first.** Animals read as one chunky mass: a short body, thick limbs and very little air under the belly.
  Legs are short and thick (the gorilla's legs are almost hidden). Use `hexa` with exact corners when a rotated box would
  poke a corner out of the silhouette.
- **Heads are BIG**: 35-60% of the body height. The head is often the highest point (gorilla) or a huge open-jawed block
  (T-Rex). When in doubt, wrap the head in `m.frame(scale=1.2-1.3)`.
- **Pose**: standing, slightly heroic. Predators get open mouths, birds and dragons raise their wings, and tails angle up or out.
- **Size**: about 8-12 studs tall for big animals and 3-6 for small ones. 1 unit = 1 stud.

## 3. Studs (studded look)
- One stud per cell: a **recessed square** about 40% of the cell, with a dark top/left lip, a light bottom/right lip and a slightly
  darker floor. It is subtle: you see it up close and it fades into texture from far away. Never draw big, high-contrast tiles.
- Cell size: `stud=0.6-0.7` for big animals (gorilla, T-Rex), `0.4-0.5` for small ones. The pattern should be dense: 5+ cells
  across a head.
- Per-stud tone variation (`jitter`): 0.03 for calm animals, up to 0.09 for "crafted" golden/earthy ones (T-Rex).
- Studs go on body, head, limbs, tail and white jaws. Leave them off eyes, brows, pupils, teeth, claws, mouth, tongue,
  nostrils and small trims (`studs=False`).

## 4. Face kit
- **Eyes**: a white rectangular block that protrudes from the face, with a square black pupil about 60-72% of the white's height,
  shifted toward the nose. Front-facing animals (apes, cats, dogs, cows) have big eyes that nearly touch. Side-facing animals
  (dinos, horses, birds) get a white "ring" with a large centred black square, often on a raised socket block.
- **Brows**: thick black (or darker body colour) bars sitting right on top of the whites. Angry animals tilt the inner end down
  about 0.2-0.3 rad. The brow is as wide as the eye or slightly wider, and about 40% of the eye's height.
- **Teeth/claws/horns**: pure white flat **blades** (`spike(..., flat=0.3)`), big and few (4-6 per jaw side), with fangs about 25% longer.
  Lower jaws of reptiles can be fully white with a saw edge of teeth.
- **Mouth** is deep crimson (`MOUTH`) and the **tongue** pink (`TONGUE`). Open mouths gape 45-55° in total.
- Muzzles and snouts are separate blocks that stick well forward of the eyes, in a lighter face colour for mammals.
  Nostrils are small dark slits, and are often omitted.

## 5. Colour
- Saturated and clean, like Roblox BrickColors pushed brighter. Palette examples:
  gorilla fur `(62, 62, 70)` / face `(98, 92, 98)`; T-Rex gold `(222, 150, 40)` / cream `(244, 240, 230)`;
  dragon red `(188, 22, 32)` / membrane `(118, 12, 24)` / belly `(214, 166, 206)`; phoenix `(236, 92, 24)` + feathers
  `(212, 52, 18)` → `(246, 128, 26)` → `(255, 222, 60)`.
- Contrast parts (belly shield, throat, muzzle, wing knobs) use a second, lighter colour, never more than 3 hues in total.
- Gradients (faceted look only): use 3 stops `(base, mid, tip)`. The tip colour must dominate the visible area, because a
  2-stop gradient reads as the muddy middle colour.
- **Mutations** (Rainbow, Gold and so on) recolour everything except the fixed colours (eye whites, pupils, brows, teeth, claws). The
  rainbow runs diagonally, with red at the head/top and magenta at the rear/feet. `<Name>_Detail.png` holds stud shading (0.5 = flat)
  and a mask (alpha 0 = keep), so an in-game mutation can multiply a colour by the detail and skip the masked cells.

## 6. Wings, feathers, fins
- Wings are huge (each one about the body's height), raised in a V and **spread sideways**, so they read from the front. A wing that
  fans only in the XZ plane is invisible from the front. Sweep the wing plane back about 35° so it also reads from the side.
- Dragon wings are a membrane `poly` (darker colour), arm and finger bones as `seg`, and a knob at the wrist.
- Bird wings are 7-9 separate blade feathers (`slab` with a 3-stop gradient). The outer feathers are the longest and point up; the inner ones lean back.
- Tails can end in decorative diamond gems (phoenix) or a spade (dragon).

## 7. Previews (what the thumbnails look like)
A bright sky-blue background, a soft ground shadow and a **thick black silhouette outline**. Inner edges have no outline;
the faceted shading carries the form. `tffa_render.py` does all of this.
