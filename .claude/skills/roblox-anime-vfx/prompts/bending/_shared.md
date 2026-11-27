# Shared rules for every bending session (read before any element prompt)

The bending game: players bend ONE element of the four-nations world (lore-accurate; not the blue-people movie). Each
class below is its own playstyle with its own mechanic, its own matter (textures/meshes) and its own moves.
**Never ship the same moveset recoloured.** `lab/bending/elements.py` is only a colour table and plumbing; a class
that reuses another class's lead shapes in a new colour is a failed class.

## Read first (every session)
1. `.claude/skills/bending-game-design/SKILL.md` + `references/lore.md` (canon limits) + `references/systems.md`.
2. `.claude/skills/roblox-anime-vfx/SKILL.md`, `references/modern-vfx.md`, `references/move-workflow.md`,
   `references/spec-format.md`.
3. `DRAGON_MOVES_NOTES.md` (every rejected attempt and why) and `lab/dragon/kit.py` + `lab/dragon/moves/*.py`
   (the template: one hand-written script per move).
4. The element's own prompt in this folder. Start `lab/bending/<element>/DESIGN.md` and
   `BENDING_<ELEMENT>_NOTES.md` (status, lessons, credits).

## References first (non-negotiable)
Before painting anything, run the `vfx-reference-frames` skill on 2-3 clips the user approves for this element (anime
fights of that element, plus anime Roblox ability showcases for the house look). Write what you see (shapes, colours,
timing, how the haze spreads) into the notes. Don't guess what a reference looks like: ask the user for a link.

## The house look (lessons from the Dragon fruit; apply from the first render)
- **Anime shape language:** sharp, tapered, hard-edged shapes; flat saturated colour, a thin white core only, a dark
  accent for the value test on sand (ink shards / a dark rim). Realistic or mesh-led looks were rejected.
- **One lead shape per move.** Hierarchy per beat: PRIMARY (frame 0-2) -> 2-3 SECONDARY shapes 1-2 frames later ->
  TERTIARY sparkles. No shared impact recipe across moves.
- **The OUTSIDE effect:** a smooth translucent haze in the element's colour spreading well past the hit, a ground haze,
  a few floating motes (`kit.aura_haze` pattern with `haze_soft`). Smooth only: no grain, no flipbook stepping.
- **Calm the clutter:** fewer, bigger, cleaner shapes; stagger lifetimes so things die in a wave; bridge the burst into
  the after-state.
- **Mass:** dust ring, debris, a ground mark that is a real object (`kit.crater`: painted bowl + slab ring + hot core).
  Ground decals y 0.04-0.1, ZOffset >= 0.
- **Abilities, not cutscenes:** one fixed gameplay camera per move; never darken the world for normal moves (ask about
  ultimates).
- **60 fps renders** (`--fps 60`). 4x4 sheets use `Grid4x4`. Size sequences: the 3rd element is the envelope.
- **Make new textures/sprites whenever a shape is missing.** Execute fixes, don't list them. Show every step (MP4 +
  strip via SendUserFile), commit and push after each step.

## Slots (every class)
M1 (a 4-hit string unique to the class), Z X C V (class moves), F (class ultimate), plus one movement tech and one
passive that expresses the class mechanic. Hit-stops 0.04-0.08 small, 0.12-0.18 big; one flash per beat.

## Steps (each waits for the user's approval)
1. References + notes. 2. Matter for this element (paint the sprites; tinted contact sheets over dark AND sand).
3. Base class moves one at a time, then each sub-class one at a time (render
   `cd lab && node render.mjs bending/<element>/moves/<spec>.json --hd --fps 60 --out out/bending`).
4. Second pass on the whole element: the classes must look DIFFERENT side by side (send a side-by-side).
5. Export only with `python3 scripts/export_luau.py --effects lab/bending/<element>/moves --merge`; check every
   manifest path exists; parse-check the modules. **Do NOT upload anything.** Meshy/Figma only if truly needed,
   estimate first.

## IP
Original names for nations, styles, teachers, places and every move (the names in these prompts are ours). No show
titles, character names, logos, insignias or named techniques in the shipped game.
