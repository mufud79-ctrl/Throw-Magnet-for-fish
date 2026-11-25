# Authoring a fruit's moveset (the loop that worked)

Use this for a hand-built fruit (one script per move). `scripts/effects.py` archetypes are a legacy 100-move
generator: don't reuse its staging for a hero fruit.

## 0. Before building
- **Research.** Pull real frames of modern games and of the element's anime reference with the
  `vfx-reference-frames` skill. Study them and write down what you see (shape, colour, staging).
  Use references for style only: never copy names or likeness from existing IP.
- **Design doc.** Write `lab/<fruit>/DESIGN.md` with the fruit's visual language (matter, palette, colour
  script, calling card, dark anchor) and per move: key, name, mechanic, *signature shape*, beat sheet with
  times, hit-stop, the BIG/medium/small elements, and its mass.
- **Notes.** Keep running notes (lessons, approval status per move) in `<fruit>_NOTES.md` next to SKILL.md.

## 1. Matter first
- Paint the fruit's own textures in `scripts/vfx_textures.py`: greyscale; layered/cel = `_glow/_rim/_mid/_core`;
  shaded = value + alpha; flipbooks 4x4 = 16 frames.
- Preview (`texture_preview.py`) and show the user a contact sheet (SendUserFile). **Wait for approval before
  building moves on new matter.**
- New hero meshes: Blender (`scripts/vfx_meshes.py`) or Meshy (estimate credits first, report spend). Rigged
  creatures: see `scripts/rig_serpent.py` (spine chain + jaw, rig layer).

## 2. One move at a time
1. `lab/<fruit>/moves/<move>.py` writes `thunder_NN_Name.json`-style specs through `kit.write()`.
2. Render HD: `cd lab && node render.mjs <fruit>/moves/<spec>.json --hd --out out/<fruit>`.
3. Make dense strips around the beats: `scripts/strip.sh <mp4> <start> <end> <out.jpg> [cols] [width]`.
   Keep strips at 8000 px or less on the long side, or SendUserFile rejects them (downscale with PIL).
4. Review against `modern-vfx.md` (checklist) and `rell-look.md`. Fix and re-render until it passes.
5. Commit and push, then **send the user the MP4 plus strips** with SendUserFile. Clicking local paths does not
   open files for them. Ask for approval and wait.
6. Approved -> next move. Rejected -> take the feedback literally, fix, show again.

## 3. Two passes
After all moves exist, do a second pass on all of them together: same style, no move whiter or busier than the
rest, consistent colour script, calling card on every move.

## 4. Ship
`python3 scripts/export_luau.py --effects lab/<fruit>/moves` -> Luau modules + `assets/upload_manifest.json`
(textures, mesh FBXs, rig models). Never upload; that's the user's call.

## Timing defaults that were approved
- Instant strikes 1-2 frames; flicker then a cooling afterglow (colour script white -> hue -> deep hue).
- Hit-stop 0.04-0.08 for small hits, 0.12-0.18 for big ones; start it ~1 frame after the strike so the frozen
  frame shows the hit.
- One inverted/mono impact frame on big hits only.
- Hand-written cameras: wide for the wind-up, push in on the hit, settle.
- PointLight brightness <= ~8 equivalent (sand floods white). Ground decals: ZOffset >= 0.
