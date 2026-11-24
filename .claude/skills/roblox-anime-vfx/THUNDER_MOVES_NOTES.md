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

## Step 2: new layer types (done, waiting for approval)
- `trail`: real Roblox Trail on two attachments riding `path` / `move` / `wave`. Ages on real time like Roblox,
  so a hit-stop holds the head and the tail keeps fading (previewer matches). Texture swapping for strip variants.
- `vbeam`: Neon/ForceField cylinder core + optional sheath + lists of crossed Beam plane sets (taper, twist,
  scroll, swap). Plane width axis in Roblox is an assumption (`PLANE_WIDTH_AXIS` in init.lua): check in Studio.
- `path` (time-keyed polyline) and `wave` (sinusoid on top, amp keys) work for every attached layer.
- Lessons: additive white on sand blooms to a white slab. Keep Neon cores thin (<= 0.2 radius), ForceField
  sheaths dim (brightness ~0.3), and give every ribbon/beam a navy alpha-blended (lightEmission 0) layer.
- Luau parse check: luaparse 0.3.1 after rewriting `x += y` (script in the session scratchpad; recreate with
  `npm i luaparse@0.3.1`). Not run in Studio.
