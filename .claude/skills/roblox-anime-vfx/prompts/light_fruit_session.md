Build the Light fruit's VFX: its matter (textures), its kit, and every move, with the same pipeline and the same bar as
the Dragon fruit (`lab/dragon/`, `DRAGON_MOVES_NOTES.md`). The ultimate is the user EMBODYING LIGHT.

## 0. Reference first (non-negotiable)
- The user's style reference is "the sword Wisteria light guy". We could NOT identify it: a web search found no
  light-sword character or style in the Roblox game Wisteria. **Do not guess what it looks like.** Ask the user for
  a video link (or the exact game, character or skill name), then run the `vfx-reference-frames` skill on it and
  study the frames before painting anything. Write down what you see (shapes, colours, timing, how the haze and
  atmosphere spread, what the ultimate looks like) in `LIGHT_MOVES_NOTES.md` and design from that.
- Also pull 2-3 anime Roblox ability showcases for the general look (the user's house style is anime-stylised:
  sharp shapes, flat hard-edged colour, white highlights, dark accents, instant pops, a transparent haze around
  the effect).

## 1. Read first
1. `.claude/skills/roblox-anime-vfx/SKILL.md`, `references/modern-vfx.md`, `references/move-workflow.md`,
   `references/spec-format.md`.
2. `DRAGON_MOVES_NOTES.md` (every rejected attempt and why: the lessons below come from it) and
   `lab/dragon/kit.py` + `lab/dragon/moves/*.py` (the template: one hand-written script per move).
3. Start `lab/light/DESIGN.md` (moves, palette, matter, beat sheets) and `LIGHT_MOVES_NOTES.md` (status, lessons).

## 2. Lessons from the Dragon fruit (apply them from the first render, not after the user complains)
- **Anime shape language, not realistic matter.** Lead with sharp, tapered, hard-edged shapes (spikes, needles,
  crescents, shards, 4-point star glints, radial speed lines), flat saturated colour with a white-hot core, and
  a dark accent (ink shards / a dark rim) so the effect passes a grayscale value test on the sand. Painted
  realistic fire/mesh-led looks were rejected ("I want anime stylized vfx").
- **One lead shape per move, never a shared recipe.** Every move must look different at a glance. Hierarchy per
  beat: PRIMARY shape (frame 0-2) -> 2-3 SECONDARY shapes 1-2 frames later -> TERTIARY sparkles/needles. Don't put
  the same speed-line burst or star flash on every hit (on Dragon only the 4 biggest hits keep speed lines).
- **The OUTSIDE effect.** The user repeatedly asked for "a transparent haze around the effect, not just the
  affected area". Every move gets the atmosphere: a big translucent glow cloud, many low-opacity SMOOTH haze puffs
  drifting out past the hit, a wide ground haze, a few floating sparks (`kit.aura_haze` pattern, `haze_soft`
  texture). It must be SMOOTH: no grainy/streaky textures, no flipbook stepping on haze (that read "rough, odd").
- **Calm the clutter.** Too many overlapping sprites read jagged. Fewer, bigger, cleaner shapes; stagger lifetimes
  so things die in a wave, not all at once; bridge the burst into the after-state (lingering glow, fading marks).
- **Ground marks are real objects.** The flat dark disc crater was rejected; the approved crater is a painted bowl
  decal (dark centre, lit rim, ink outline, radial cracks) + a ring of rock slabs + a hot core that cools
  (`kit.crater`). Ground decals: y 0.04-0.1, ZOffset >= 0 (negative sinks under the floor and vanishes).
- **Abilities, not cutscenes.** One fixed gameplay camera per move (or a gentle follow); no cinematic moves, and
  never darken the sky/world for normal moves. Ask the user whether the ULTIMATE may dim the world.
- **Smooth playback.** Render at 60 fps (`--fps 60`). Loop flipbooks that must run long; 16-frame one-shots stretched
  over long lifetimes step visibly.
- **Texture gotchas.** 4x4 sheets need `FlipbookLayout: Grid4x4` (layout None shows the whole grid as dots);
  a single soft blob is its own single-image texture. Emitter Size sequences: the 3rd element is the envelope,
  never an ease string. `Disc` emits upward: ground rings use Cylinder / Surface / Outward.
- **Glints/sparkles near the effect.** Scatter radius about 1x the effect radius; far ones land on the camera.
- **Make new textures/sprites whenever a shape is missing** (`scripts/vfx_textures.py`, preview with
  `scripts/fire_preview.py`-style tinted sheets over dark AND sand). Don't force an existing sprite to fit.
- **Execute, don't list.** When the user says it looks bad: find the concrete causes, fix them, re-render, show.
- **Show every step:** MP4 + frame strip via SendUserFile; commit and push after each step.

## 3. Light matter and palette (proposal: confirm against the reference frames)
- Colour script: white core #ffffff -> pale gold #fff3b8 -> gold #ffd24a -> warm amber rim #ffb43a, with a DARK
  accent for value (deep indigo #1c1a3a ink shards / outlines) and an optional prismatic edge (pale cyan
  #9fe8ff / lavender #c8b0ff) only if the reference shows it. Light is additive: keep the core thin and use the
  dark accent + haze so it doesn't blow out to a white blob on the sand.
- New sprites (layered `_glow/_rim/_mid/_core` unless noted): `light_needle` (long razor ray), `light_lance`
  (thrown spear with a hot tip), `light_slash` (thin crescent with a bright inner line), `light_burst` (radial
  star of rays), `light_ring` (thin hard ring), `prism_shards` (angular facets), `light_afterimage` (a streaked
  silhouette smear), `light_halo` (thin rotating halo with rune-like tick marks, single image), `light_dust`
  (floating motes, random frames), reuse `haze_soft`, `anime_glint`, `speed_burst`, `ink_shards`,
  `impact_crater`.

## 4. Moves (proposal: original names, no IP names or signature attacks; confirm with the user first)
- **Z Photon Lance**: forms a spear of light in the hand and hurls it; it streaks in a straight line and pins the
  target in a starburst. Lead shape: the lance + its razor trail.
- **X Flashstep**: a light-speed dash (teleport) leaving a streaked afterimage and a line of delayed light cuts
  that pop a beat later along the path. Lead shape: the afterimage line.
- **C Prism Volley**: a fan of light needles fired from the fingertips in rapid bursts, each hit a tiny star.
  Lead shape: the needle fan.
- **V Sunfall**: points up; a column of light slams down on the target zone from the sky, leaving a glowing
  crater. Lead shape: the vertical column.
- **B Mirror Halo**: a ring of floating light mirrors/halos around the caster that fire rays inward/outward.
  Lead shape: the halo ring.
- **F ULTIMATE: Lightborne (the user embodies light)**: the user's body turns into light: the avatar becomes a
  glowing white-gold silhouette (rig/avatar tint + transparency + an outline glow), light motes and a halo form
  around it; it blinks between several targets at light speed (each blink = afterimage streak + a hit star),
  ends with the user hovering, a burst of rays from the body, and returns to normal. Lead shape: the body made
  of light. Needs avatar tint/transparency keys on the caster (check `lab/page/vfx.js` / `init.lua`; if missing,
  add them in BOTH and parse-check the Luau with luaparse; say it hasn't been run in Studio).

## 5. Steps (show each and wait for approval)
1. Reference frames + written notes (section 0). 2. Matter: paint the sprites, send tinted contact sheets.
3. `lab/light/kit.py` (copy the Dragon kit's plumbing: stacks, aura_haze, crater, ink, needles, speed_lines,
   dark_haze, cr_path; light palette + conventions in `write()`). 4. Moves one at a time
   (`lab/light/moves/<move>.py` -> `light_NN_Name.json`, render
   `cd lab && node render.mjs light/moves/<spec>.json --hd --fps 60 --out out/light`). 5. Second pass on all,
   side-by-side. 6. Export ONLY with `--merge` (the plain command deletes every other exported effect):
   `python3 scripts/export_luau.py --effects lab/light/moves --merge`, check every manifest path exists,
   parse-check the modules. **Do NOT upload anything.**
- Meshy or Figma generation only if a move truly needs a new asset: estimate first and report the spend.
