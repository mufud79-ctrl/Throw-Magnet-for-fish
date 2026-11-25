Build a new devil fruit for my Roblox game: the **Dragon Fruit (hybrid + full form)**. That's a hybrid moveset, a
transformation, and a full-form moveset where you ARE a rigged dragon, all as VFX. Same bar as the thunder
fruit (the user called the modern pass "so much better").

## Read first (non-negotiable)
1. `.claude/skills/roblox-anime-vfx/SKILL.md`
2. `references/modern-vfx.md`: what modern (TSB / Jujutsu Shenanigans / Type Soul) looks like, the layer
   conventions, and 10 failure modes that already happened. Do not repeat them.
3. `references/move-workflow.md`: the loop (design doc -> matter -> one move at a time with approval -> two
   passes -> export).
4. `THUNDER_MOVES_NOTES.md`: every rejected thunder attempt and why. `lab/thunder/kit.py` is the toolkit template.
   `scripts/rig_serpent.py` + the `rig` layer show how the Meshy serpent was rigged (spine chain + jaw) and
   played along a path.
5. Use the `vfx-reference-frames` skill before designing. Pull real frames of modern dragon transformations and
   fire VFX: e.g. "roblox dragon transformation showcase", "roblox dragon fruit rework showcase",
   "the strongest battlegrounds showcase", "anime dragon breath scene", "roblox fire vfx showcase". Study them
   and write what you learn into the design doc.

## Working rules
- Show me everything and wait for my approval before moving on. Send MP4s, frame strips and texture contact
  sheets with SendUserFile (clicking local paths doesn't open files for me). Strips must be <= 8000 px.
- Each move gets its own mechanic and signature shape. One visual language for the whole fruit. No shared
  impact recipe, no templated staging, no `scripts/effects.py` archetypes.
- Follow the five animation rules on every move. Hit-stops: 0.04-0.08 small, 0.12-0.18 big. One inverted/mono
  impact frame only on big hits. One flash per beat, 1-2 frames.
- Paint new matter greyscale and show me the sheets before using them. Meshy costs credits: estimate first, keep
  it to what's needed, report the spend. The API key is in the environment's secret store, injected by the
  proxy; send `Authorization: Bearer proxy-injected`.
- Commit and push after each step. Work on the branch this session is assigned.
- Original design: no names, characters or likeness from One Piece, Blox Fruits or any other IP. No azure
  eastern dragon like a certain emperor, and no copying an existing game's dragon.
- Final step after everything is approved: `python3 scripts/export_luau.py --effects lab/dragon/moves` and update
  the upload manifest (textures, meshes, rig models). Do NOT upload anything; that's my call.
- Notes go in `.claude/skills/roblox-anime-vfx/DRAGON_MOVES_NOTES.md`.

## Visual language (refine in the design doc)
- Original dragon: a **crimson-and-gold flame dragon** with obsidian-black scales, glowing ember seams between the
  scales, gold horns, and wing membranes lit from inside like embers.
- Matter: modern stylised fire (painted billowing flame with a white-gold core -> orange -> crimson rim, torn
  tongues, ember flakes), black smoke as the dark anchor, molten cracks.
- Colour script: white-gold -> orange -> crimson -> charcoal as fire cools.
- Calling card: scorched claw gouges / molten cracks in the ground that glow and cool, with drifting embers.
- The world dims warm-dark during the full form, so it owns the frame.

## Why this is hard (solve these deliberately)
- **A rigged full dragon with wings.** Meshy model -> custom rig: spine chain, jaw, neck, tail, legs, and **wing
  bones that flap** (the membrane folds and unfolds). The current `rig` layer only drives a spine along a path
  plus a jaw. Extend it, in the previewer `lab/page/vfx.js` AND the Luau
  `templates/ReplicatedStorage/AnimeVFX/init.lua`, with generic per-bone keyframe tracks (rotation keys per named
  bone) layered on top of the path-follow. Validate in the previewer and keep the Luau parse-checked.
- **Hybrid form on the player.** Claws, horns, wings and a tail attached to the character for the hybrid moves:
  meshes attached to the avatar's limbs that follow its pose. In Luau, they attach to the character.
- **The transformation.** A flame cocoon, the silhouette swells, the full dragon bursts out with a roar
  shockwave. The rig reveal must not pop.
- **Fire that reads modern on bright sand**, not orange blobs: hierarchy, mass (black smoke, embers, molten
  rocks), saturation without white-out.
- **Breath beams** that feel like a torrent (a volumetric flame beam plus ground scorching along the sweep), not
  a laser.

## Moveset (refine it in the design doc; keep each mechanic distinct)
**Hybrid form** (horns, clawed arms, half-wings, tail)
| key | move | mechanic / signature |
|---|---|---|
| Z | **Talon Rend** | triple claw slash: three burning crescent rakes that leave glowing gouges in the air and the ground |
| X | **Wing Buffet** | the wings snap open: a wall of flame-wind shoves enemies back, embers riding the gust lines |
| C | **Sky Drop** | leap with wing beats, dive back down claws-first: crater, molten cracks, ring of fire |
| V | **Tail Cyclone** | 360 tail sweep leaving a burning ring that erupts in flame pillars |
| B | **Ember Breath** | the jaw morphs: a short cone of breath that scorches the ground in a fan |
| F | **Transform** | flame cocoon -> the silhouette swells -> the full dragon bursts out and roars (shockwave rings, dust ring, rocks) |

**Full form** (you ARE the rigged dragon: flying, wings flapping, jaw, tail)
| key | move | mechanic / signature |
|---|---|---|
| Z | **Inferno Torrent** | a charged breath beam that sweeps the ground, erupting a line of fire behind it |
| X | **Comet Dive** | climb, fold the wings, dive as a burning comet: huge crater, shockwave, molten rock rain |
| C | **Firestorm Wings** | hovering wing beats whip up a fire tornado around the dragon |
| V | **Dragon Roar** | roar: visible sound/heat rings, a ground ripple, enemies stunned and pushed back |
| B | **Ash Rain** | circling overhead, fireballs rain down in a pattern, each leaving a small crater |
| F | **Revert** | the dragon collapses into flame and the player drops out, embers settling |

## Suggested order
1. Research, then write `lab/dragon/DESIGN.md` and show it to me.
2. Make a concept sheet for the dragon (Figma image generation or a painted sheet) and show it to me.
3. Build the Meshy model and rig (wings!), extend the rig layer with bone tracks, and show me a flap cycle and a
   dive.
4. Paint the fire matter and show it to me.
5. Build the hybrid moves Z..F one at a time, with my approval on each.
6. Build the full-form moves Z..F one at a time, with my approval on each.
7. Do a second pass on everything.
8. Export and update the manifest (no upload).
