Build a new devil fruit for my Roblox game: the **Glass Fruit**, 7 base moves (Z X C V B N M) as VFX, to the same
bar as the thunder fruit we just finished (which the user called "so much better" after the modern pass).

## Read first (non-negotiable)
1. `.claude/skills/roblox-anime-vfx/SKILL.md`
2. `references/modern-vfx.md`: what modern (TSB / Jujutsu Shenanigans / Type Soul) looks like, the layer
   conventions, and 10 failure modes that already happened. Do not repeat them.
3. `references/move-workflow.md`: the loop (design doc -> matter -> one move at a time with approval -> two
   passes -> export).
4. `THUNDER_MOVES_NOTES.md`: every rejected thunder attempt and why. `lab/thunder/kit.py` is the toolkit template.
5. Use the `vfx-reference-frames` skill before designing. Pull real frames for glass and crystal VFX in modern
   Roblox games and anime (queries like "roblox glass vfx", "roblox crystal ability showcase", "anime glass
   shatter scene", "the strongest battlegrounds showcase", "type soul showcase"). Study them and write what you
   learn into the design doc.

## Working rules
- Show me everything and wait for my approval before moving on. Send MP4s, frame strips and texture contact
  sheets with SendUserFile (clicking local paths doesn't open files for me). Strips must be <= 8000 px.
- Each move gets its own mechanic and signature shape. One visual language for the whole fruit. No shared
  impact recipe, no templated staging, no `scripts/effects.py` archetypes.
- Follow the five animation rules on every move. Hit-stops: 0.04-0.08 small, 0.12-0.18 big. One inverted/mono
  impact frame only on big hits. One flash per beat, 1-2 frames.
- Paint new matter greyscale and show me the sheets before using them.
- Commit and push after each step. Work on the branch this session is assigned.
- Original fruit: no names, characters or likeness from One Piece or any other IP.
- Final step after all 7 are approved: `python3 scripts/export_luau.py --effects lab/glass/moves` and update the
  upload manifest. Do NOT upload anything; that's my call.
- Notes go in `.claude/skills/roblox-anime-vfx/GLASS_MOVES_NOTES.md`.

## Why this fruit is hard (solve these deliberately)
- **Clear glass reads as nothing (or white) on bright sand.** Everything that worked for thunder (glow, bloom,
  additive light) works against glass. Sell it with **edges and glints**: bright thin edge highlights, dark
  smoked facets (the dark anchor), refraction cues (offset/tinted copies of what's behind, Roblox `Glass`
  material shells, darker rims), and sharp specular glints that ping on and off as shards tumble.
- **Prismatic dispersion without a toy rainbow.** Keep the colour mostly clear/aqua; spectral colour (thin
  cyan/magenta/gold split) only on the hottest edges and on the prism move.
- **Hundreds of crisp shards.** Faceted shard meshes (Blender) + flipbook shard sprites with per-frame glints;
  physics arcs, tumble, ground bounce, glittering dust that twinkles where they land. Keep it readable:
  BIG/medium/small hierarchy, not noise.
- **Cracking the air itself.** World-space crack sheets that spread across empty space, then the "pane" of
  space shatters into big reflective shards.
- **Reassembly.** Reverse-shatter (shards flying back together into a body).

## Visual language
- Matter: clear glass with white-hot edges, pale aqua body tint, smoked blue-grey facets; spectral fringe only
  at peak moments.
- Colour script: white glint -> pale aqua -> teal -> smoked grey-blue as things cool or crumble.
- Calling card: glittering glass dust + a radial fracture mark on the ground that catches light and twinkles
  for a few seconds.
- Dark anchor: smoked-glass facets and lead lines (the dark seams on the stained-glass move).

## Moveset (refine it in the design doc; keep each mechanic distinct)
| key | move | mechanic | signature |
|---|---|---|---|
| Z | **Shard Volley** | flick: a fan of 7 spinning glass knives | spinning knives with refraction streak trails; each hit bursts into chips + glints |
| X | **Prism Ray** | a prism forms at the palm; a white beam enters and splits into a sweeping spectrum fan | dispersion: one beam in, a 3-band fan out |
| C | **Shatter Step** | the caster turns to glass, shatters into a shard cloud that streaks forward and reassembles at the destination | reverse-shatter reassembly |
| V | **Thorn Garden** | stomp: a fracture runs along the ground and rows of faceted glass spikes erupt in sequence, then crumble to glittering dust | sequential spike eruption + crumble |
| B | **Mirror Maze** | 6 hex mirror panes snap around the target; each shows a flickering copy of the caster; all copies strike inward; the panes shatter | mirror copies converging |
| N | **Rose Window** | a giant stained-glass rose window builds overhead pane by pane (coloured panes, dark lead lines), then drops and shatters into a rain of coloured shards | stained-glass build-up + shatter rain |
| M | **Worldbreak** | punch the air: the AIR cracks (huge spreading world-space cracks), a beat of silence, then the pane of space shatters outward in huge sky-reflecting shards at the enemies; mono impact frame | cracking empty space |

## Suggested order
Research -> `lab/glass/DESIGN.md` -> show me the design -> paint glass matter (shard sprites with glints,
glitter dust, fracture mark, crack sheet, prism/spectrum strip, stained-glass panes) and build meshes (faceted
shards, spikes, hex pane, prism) -> show me -> build moves Z..M one at a time with my approval -> second pass on
all 7 -> export + manifest (no upload).
