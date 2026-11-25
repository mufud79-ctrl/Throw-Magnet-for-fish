First run: git fetch origin claude/dragon-fruit-vfx-k354ta && git merge --no-edit FETCH_HEAD
(it has the design doc, the dragon concept art and the brief). Then build the Dragon fruit VFX.

## Read first
1. `.claude/skills/roblox-anime-vfx/prompts/dragon_fruit_session.md`: the original brief (working rules, quality
   bar, moveset, export). Its rules all still apply, EXCEPT the dragon is now an Eastern serpent dragon emperor
   (wingless). Ignore every mention of wings, half-wings and wing flaps.
2. `.claude/skills/roblox-anime-vfx/lab/dragon/DESIGN.md`: the design doc. The "Revision v3b", "v3" and "v2" blocks at
   the top override the rest: wingless serpent, legs and whiskers instead of wings, and the move swaps (Horn Rush,
   Firestorm Coil, coil-out transform, coil-and-collapse revert).
3. `.claude/skills/roblox-anime-vfx/DRAGON_MOVES_NOTES.md`, `references/modern-vfx.md`,
   `references/move-workflow.md`, `THUNDER_MOVES_NOTES.md`, `lab/thunder/kit.py`, `scripts/rig_serpent.py`.

## The dragon (concept APPROVED; the hybrid look is hybrid_r15_v2.png)
- Look: `assets/source_art/dragon/dragon_hero_v3.png`. Model sheet: `dragon_sheet_v3.png`. Meshy inputs:
  `v3_view_side.png`, `v3_view_top.png`, `v3_view_front.png`.
- Design: as close to the classic wingless Eastern dragon emperor as possible while staying original. Deep azure/
  teal scales, a pale cream belly band, cream-gold ridged horns (plus a back pair) and talons, a dark navy curl
  mane and tail fan, long blue whiskers, yellow eyes, a broad bulbous nose, a spiral-carved brow, a scarred snout,
  a huge toothy grin. Never use names, logos or signature attacks from any existing IP.
- VFX colours stay fire (white-gold, orange, crimson, char, with black smoke): orange fire against the blue body.
- **Hybrid = add-on accessory pieces on the player's normal R15 body, never a replacement model.** Aggressive look,
  `hybrid_r15_v2.png` (DESIGN.md "Revision v3b"): hooked horns, a back pair and a spike crest on Head; a navy curl
  mane collar and a back spine ridge on UpperTorso; spiked scale pauldrons on the upper arms; bladed scale
  forearm armour; **clawed hands with 5 jointed fingers and hooked talons** (skinned, finger bones so the claws curl
  and rake); and a spiked skinned tail on LowerTorso. Each piece is welded to its R15 part and follows the player's
  own animation. Model the pieces in a neutral pose (the sheet's stance is a look reference).

## Steps (show me each one and wait for my approval; send MP4s, strips and contact sheets with SendUserFile,
## strips <= 8000 px; commit and push after each step on the branch this session is assigned)
1. **Model.** Meshy multi-image-to-3D from the three v3 views (about 30 credits). Hybrid pieces: horns and tail
   are cut from the dragon model and reshaped in Blender to match `hybrid_r15_v2.png` (hooked horn tips, spike
   crest, tail spikes and a blade tip), which is free. Use a Meshy crop instead only if the reshaped piece doesn't
   read. The collar, pauldron, forearm armour and claw hand come from Meshy
   image-to-3D of clean crops of `hybrid_r15_v2.png` (about 4 x 20-30). Total estimate about 130 credits, cap 170:
   estimate before each job and report the spend. The key is in the environment's secret store, injected by the proxy: send
   `Authorization: Bearer proxy-injected`. Show me a turntable of the raw model.
2. **Rig.** Write `scripts/rig_dragon.py` based on `rig_serpent.py`: head toward -Z, about 30 studs long, about
   10k tris, the mouth cut on the lip line with a palate and fangs, `spine_00..19` + `jaw`, 4 short legs
   (`legFL/FR/BL/BR_0/1`) and whiskers (`whiskerL/R_0..2`). Cut the hybrid horns and a spiked 6-7 bone tail from the same model.
   Rig the claw hands with `finger1..5_0/1` bones.
   Fit all hybrid pieces to the R15 rig (scale and offsets per part) and export them as separate meshes.
3. **Rig layer v2**, in the previewer `lab/page/vfx.js` AND the Luau `templates/ReplicatedStorage/AnimeVFX/init.lua`:
   `follow: "path"|"rigid"`, generic per-bone rotation tracks (`boneTracks`, with `loop` and `mirror`),
   bone-riding emitters, trails and lights (`bone: {rig, name, offset}`), and an `attach` layer for hybrid pieces
   on the avatar (Luau: welded to Head / UpperTorso / hands / LowerTorso, Bone.Transform tracks). Keep the Luau
   parse-checked with luaparse, and say that it hasn't been run in Studio. Show me an S-coil swim through the
   sky, a coil-up then head-first dive, a roar (jaw and whiskers), and the hybrid pieces on the avatar.
4. **Fire matter.** Paint the new greyscale sheets listed in DESIGN.md (flame_billow, flame_tongue,
   flame_strip_1..4, claw_rake, fire_crescent, fire_ring, fire_impact, molten_crack, claw_gouge, heat_ring) in
   `scripts/vfx_textures.py`. Show me a contact sheet and tinted previews before using them.
5. **Kit.** Write `lab/dragon/kit.py` from `lab/thunder/kit.py` with the fire palette and layer conventions
   (rim crimson LE 0.2, cooling to char) and the warm-dark grade.
6. **Hybrid moves** Z Talon Rend, X Horn Rush, C Sky Drop, V Tail Cyclone, B Ember Breath, F Transform, one at a
   time in `lab/dragon/moves/`. Render HD, review against the modern-vfx checklist, then send the MP4 plus strips
   and wait for my approval on each.
7. **Full-form moves** Z Inferno Torrent, X Comet Dive, C Firestorm Coil, V Dragon Roar, B Ash Rain, F Revert, one
   at a time with my approval on each.
8. **Second pass** on all 12 together.
9. **Export.** Run `python3 scripts/export_luau.py --effects lab/dragon/moves` and update the upload manifest
   (textures, meshes, rig models). Do NOT upload anything.

Keep notes, approval status and credit spend in `DRAGON_MOVES_NOTES.md`.
