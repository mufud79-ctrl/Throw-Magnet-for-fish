---
name: vfx-reference-frames
description: Pull real frames from YouTube gameplay/showcase videos (e.g. The Strongest Battlegrounds, Jujutsu Shenanigans, Type Soul, RELL Seas, anime fights) into contact sheets to study what modern VFX actually looks like before designing or critiquing effects. Use before building or reworking any VFX, when the user says effects look dated/lame/off-style, or when they name a game or anime to match.
---

# VFX reference frames

Describing "modern VFX" from memory produced effects the user called "from 2015". Looking at real frames fixed
it. Always look before you build or redesign.

## Pull frames
```sh
.claude/skills/vfx-reference-frames/scripts/ref_frames.sh OUT_DIR 6 \
  "the strongest battlegrounds new character showcase" \
  "type soul shikai showcase" \
  "jujutsu shenanigans vfx" \
  "roblox vfx showcase lightning"
```
For each query it prints `OUT_DIR/sheet_N.jpg`: rows = videos, cols = YouTube's published auto-frames at
25/50/75%. Open the sheets with Read and study them. Put OUT_DIR in the scratchpad: these are untrusted
downloads, so don't commit them.

- YouTube blocks headless playback with a CAPTCHA. Don't try to bypass it; the auto-frames + thumbnails are
  enough. Some rows will be facecams or menus; ignore them, or add `vfx`/`showcase`/`ability` to the query.
- Good queries: `<game> <character/move> showcase`, `<game> awakening`, `roblox <element> vfx`,
  `<anime> <technique> scene`.
- Use references for style only. Never copy a game's or anime's names, characters, logos or exact designs.

## What to write down (then act on it)
For each element or game, note: glow treatment (additive? outlines?), how the world is graded during the move,
the BIG/medium/small shapes at the hit, mass (smoke style, debris, ground marks), streaks/speedlines, colour
script, how long flashes last, camera behaviour. Then compare your own frames side by side (ffmpeg xstack)
before showing the user.

See `../roblox-anime-vfx/references/modern-vfx.md` for what these studies already taught.
