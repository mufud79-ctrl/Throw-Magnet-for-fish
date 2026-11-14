---
name: roblox-stylised-models
description: Style guide for making 3D models for Roblox simulator-style games: stylised cartoon creatures (smooth, big-eyed, painted texture) and blocky Roblox-part builds (studded bricks, chunky rounded parts) for animals, props and environments. Use when asked to model, generate or script (e.g. Blender Python) a creature, pet, fish, animal, bait, tool or environment prop for a Roblox game, or when the user asks for "the style", "the blocky style" or "the cartoon fish style".
---

# Roblox stylised models: style guide

Two approved looks. Choose one per asset family and keep the whole family in that look. If the user hasn't said which, ask once:
- **Style A: Smooth cartoon** for hero creatures that get held, shown off or collected (fish, pets, baits).
- **Style B: Blocky parts** for environments, props and tameable animals that should read as Roblox "parts".

Rules that apply to both styles come first. The rules for each style follow.

---

## 1. Shared rules (always)

**Readability first**
- The asset must be recognisable from its silhouette alone at a small size. Exaggerate the one or two features that identify it (a hammerhead's head, a T-Rex's tiny arms, a frog's bulging eyes).
- Give it chunky, simple masses and few thin bits. Anything thinner than about 0.15 studs disappears in game.
- Check it from three views: **hero 3/4**, **side** and **front**. Dramatic assets sell on their front silhouette, so always render a front view for them.

**Rarity shows through design, not only colour**
- Common: plain, natural and recognisable, with few parts. Small (fish about 1.6–3 studs long).
- Each rarity step adds parts, drama, sharper shapes and effects. Top tiers reach about 6–7 studs for fish and bigger for animals.
- **Rare and above must look aggressive and cool, not cute.** Think "1998 Mazda vs. M5 Competition": sharp, swept-back shapes, angry brows, slit pupils, teeth, spikes, menace. Don't reuse one body with a recolour. Give each one new shapes.

**Eyes are the personality**
- Big and expressive. Common or friendly creatures get round eyes with a white, a pupil and a glint.
- Aggressive ones get angry brows that slope down toward the snout, slit or narrowed pupils, a coloured iris, and optionally glowing eyes.

**Colour**
- Bright, saturated and slightly toy-like. Use natural colours for commons and fantasy colours for higher tiers.
- Use a light belly or underside and a darker back: it gives free depth.
- Keep a limited palette of about 3–5 main colours per asset.

**Glow (only where it makes sense)**
- Use glow for lures, lava cracks, photophores, runes, auras, magic eyes, star spots and nothing else.
- Put all glowing parts in a **separate mesh named `<Name>_Glow`**, with **one glow colour per asset**. In Roblox, set that MeshPart to `Material = Neon` and `Color` = the glow colour.
- Record each glow colour in a table (asset → glow parts → hex) so whoever imports the asset knows what to set.

**Roblox technical rules**
- Scale is 1 unit = 1 stud. The model faces Roblox forward (-Z), so in Blender build it facing +X and export with the right axis conversion.
- Keep each mesh under **20k triangles** (Roblox's limit per MeshPart). Aim much lower: about 5–7k for small items and commons.
- Use one texture atlas per asset (1024²). Export **.glb** (the main import format, texture embedded), plus .fbx and the source .blend.
- Studs are an optional texture swap. Ship `<Name>_Texture.png` (clean) and `<Name>_Texture_Studs.png` (the same texture with a stud tile multiplied over it; the default stud cell is 0.15 studs on smooth models). The stud tile is in `assets/stud.png` (a 4×4 grid of studs).
- Static props have no rig. Creatures get a simple rig and a shared set of clips (Idle, Swim/Walk, Sprint, Hooked/Hit, Flop, Showcase), with family variants where the motion differs (eels, rays).

**Folder layout**
```
models/<Category or Rarity>/<Name>/
  <Name>.glb  <Name>.fbx  <Name>.blend
  <Name>_Texture.png  <Name>_Texture_Studs.png
  previews/ (hero, side, front, hero_studs)
```

---

## 2. Style A: smooth cartoon

The look is a stylised cartoon with **smooth shading**, readable chunky silhouettes and a hand-painted feel.

- **Body:** a lofted, smooth body with a clear taper. Give fish a slight swim curve in the tail so they never look stiff.
- **Eyes:** an iris sphere, a pupil and a white glint. Make them large, about 1/4 to 1/3 of the head height.
- **Painted texture detail (no geometry for small details):** scales, patterns (bars, stripes, spots, speckles, bands), and fin rays that fade toward pale, almost translucent tips. Add soft gradients from a dark back to a light belly.
- **Fins and extras:** keep fins as clean, thick shapes and avoid paper-thin planes. Add barbels, whiskers, frills and crests as extra parts on rarer creatures.
- **Aggressive kit for Rare and above:** an open jaw with pyramid teeth, angled brows, slit pupils, sharp swept-back fins, blade-like wings, spikes, glowing crack lines, gill slits and a halo or aura. Make each top-tier creature a custom build, not a template.
- **Avoid:** realistic proportions, faceted low-poly shading, dull muddy colours and over-detailed geometry.

---

## 3. Style B: blocky Roblox parts

The look is a model **assembled from Roblox-style parts**: blocks, wedges, cylinders and balls in flat bright colours. It belongs to the same visual family as popular Roblox simulator and tycoon games. Rejected alternatives were smooth sculpted props and faceted low-poly props. Don't drift into either.

**Parts**
- **Block:** the main building piece. It has a stud texture on its faces (1 stud per cell for big environment parts; denser studs on creatures).
- **Wedge:** for slopes, claws, toes, beaks, roof pitches and tail spades.
- **Cylinder and ball:** smooth plastic, with no studs. Use them for eyes, wheels, joints and teeth (4-sided cones make sharp pyramid teeth).
- **Segmented curves:** make curves from a chain of short blocks or cylinders with ball joints. Allow only minimal real curvature.
- **Rounded chunky variant (for creatures):** bevel the outer box edges slightly (soft, toy-like parts) and taper limb blocks (wide at the thigh, narrow at the ankle). It still reads as parts, just friendlier.

**Studs**
- Put studs only on **big body parts**: body, chest, thighs, tail segments and big rocks.
- **Face details stay smooth:** eyes, pupils, brows, nostrils, mouth, teeth, stripes and spots are thin flat plates with no studs.

**Creature anatomy recipe (animals)**
- Body = core block + shoulder block + hip block (slightly rotated so the back isn't one flat box) + a lighter belly plate.
- Legs = thigh block → narrower leg block → a darker foot block.
- Head = head block + jaw block + snout block + a black nose plate.
- Eyes = a white plate, a black pupil plate set toward the front, and a thick black brow plate (tilted down-inward when angry).
- Ears, tails and patterns come from a small library of types (pointed, round, long, floppy, big, tiny; short, long, bushy, curly, tufted, flat, thick, dragon; stripes, spots, patches, saddle). Mix and match types and recolour them for variety, but give hero animals unique shapes.
- **Angry or predator variant:** a deep cranium, wide cheeks, a tapered snout, a dark eye socket with an orange iris, a slit pupil and a glint, an open hinged jaw with a red mouth, a tongue, evenly spaced sharp teeth growing to a fang, and heavy brows sloping toward the snout.

**Environment props**
- If the scene has fog or water, colours must punch through it: light tops, tall silhouettes, bright saturated parts and Neon accents.
- Props must fit the setting (for example underwater: sunken versions, things seen from below, bubbles).
- Don't repeat a prop across zones. Make about 6 unique props per zone, each themed to it.

**Colour palette:** use Roblox-style BrickColor tones, for example white `#F2F3F3`, black `#1E2026`, red `#C4281C`, orange `#E68232`, yellow `#F5CD30`, green `#4B974B`, lime `#8CC846`, blue `#0D69AC`, cyan `#28BEEC`, purple `#6232C8`, pink `#FF98DC`, brown `#7C5C46`, sand `#D7C59A` and gold `#EFB838`. Use at most about 32 colours per asset.

---

## 4. Workflow (keeps output consistent and cheap)

1. **Build one style reference asset first** and get the user's approval. Treat it as locked: never change it afterwards. Every later asset is compared against it.
2. Build in batches, one script per family or rarity (a spec dict per asset feeding shared builders).
3. Render a **contact sheet** of the hero views per batch and review that one image, not every render. Do at most one fix round per batch.
4. Check triangle counts and glow meshes, and update the glow-colour table.
5. Keep a running handoff or status note (what's done, approved rules, what's weak) so a new session can continue in the same style.

## 5. Quick checklist before delivering an asset
- [ ] Recognisable from its silhouette (hero, side and front views).
- [ ] Its rarity is obvious from the design, and Rare and above look aggressive.
- [ ] The eyes have personality (glint for friendly; brow and slit pupil for angry).
- [ ] The style is consistent with the reference asset (A or B, not a mix).
- [ ] Under 20k triangles; 1 unit = 1 stud; faces forward.
- [ ] Glow is in a separate `_Glow` mesh, one colour, recorded in the table.
- [ ] Clean and studded textures, plus .glb, .fbx and .blend, are exported.
