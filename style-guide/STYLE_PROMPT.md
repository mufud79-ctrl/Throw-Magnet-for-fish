# Copy-paste style prompt

Paste this at the start of a chat with Claude (or any AI). Keep the version that matches what you're making.

---

## Version A: smooth cartoon creatures (fish, pets, collectibles)

I'm making 3D models for a Roblox simulator game. Please follow this style exactly:

- **Look:** stylised cartoon with smooth shading and readable, chunky silhouettes. No realism and no faceted low-poly.
- **Eyes:** big and expressive, with an iris, a pupil and a white glint. Friendly creatures get round eyes. Aggressive ones get angry brows sloping toward the snout and slit pupils.
- **Detail is painted, not modelled:** scales, stripes, spots, and fin rays that fade to pale tips, with a dark back and a light belly. Fish get a slight swim curve in the tail.
- **Rarity shows through design:** commons are plain, natural and small (about 1.6–3 studs). Each rarity adds parts and drama, up to about 6–7 studs. **Rare and above must look aggressive and cool, not cute.** Use sharp, swept-back shapes, teeth, spikes, menace. Think "M5 Competition, not a 1998 Mazda". Every high-tier creature gets unique shapes, not a recoloured body.
- **Glow only where it makes sense** (lures, lava cracks, photophores, magic eyes). Put it in a separate `<Name>_Glow` mesh with one colour per model (set to Neon in Roblox), and tell me the hex colour.
- **Roblox specs:** 1 unit = 1 stud, facing forward, under 20k triangles per mesh (aim for about 5–7k on commons), one 1024 texture atlas, export .glb, .fbx and .blend. Also make a second texture with a stud pattern multiplied on top (`<Name>_Texture_Studs.png`).
- Show me hero (3/4), side and **front** renders. The front silhouette matters for dramatic models.

---

## Version B: blocky Roblox-part style (animals, props, environments)

I'm making 3D models for a Roblox simulator game. Please follow this style exactly:

- **Look:** built from Roblox-style parts: blocks, wedges, cylinders and balls in flat, bright BrickColor colours, like the classic simulator and tycoon look. **Not** smooth sculpted and **not** faceted low-poly.
- **Studs** (classic Roblox stud texture) go on the big parts only: body, chest, thighs, tail and rocks. Face details stay smooth: eyes, pupils, brows, nostrils, mouths, teeth, stripes and spots are thin flat plates.
- **Creatures:** body = core + shoulder + hip blocks (slightly angled) + a lighter belly plate. Legs = thigh → narrower leg → darker foot. Head = head + jaw + snout + black nose. Eyes = a white plate, a black pupil toward the front, and a thick black brow (tilted down-in when angry). For a softer toy look, bevel the box edges a little and taper the limbs.
- **Predators and high rarity:** deep head, open hinged jaw with a red mouth, evenly spaced pyramid teeth growing to fangs, an orange eye with a slit pupil in a dark socket, and heavy angry brows. Cool and aggressive, not cute.
- Curves come only from short segmented blocks with ball joints.
- **Environment props** must fit the setting and read clearly. If there's fog or water, use light tops, tall silhouettes, saturated colours and Neon accents. Don't repeat a prop between zones.
- **Glow** goes in a separate `<Name>_Glow` mesh with one colour per model (Neon in Roblox).
- **Roblox specs:** 1 unit = 1 stud, facing forward, under 20k triangles per mesh, one texture atlas, export .glb, .fbx and .blend.
- Show me hero (3/4), side and front renders.

---

**Tip:** make ONE reference model first, get it exactly right, then say "match the style of <reference> for all the rest". Review batches on one contact sheet instead of one image per model.
