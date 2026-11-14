# Prompt: import the CURRENT Cannon Tame models into Roblox

Paste everything below the line into the Roblox import/showcase session.

---

The models you imported are outdated. They are the very first Cannon Tame prototype (commit `636292e`): e.g. the Chicken
with ONE red comb block, a black eye with a white glint and no brow, and a giant recessed "L" square per face. Those files
only exist in the HISTORY of `claude/roblox-animal-models-852c5h`; the branch's current files are completely different.
Your working tree is sitting on old files (your branch was cut from `636292e`, so a pull/merge can keep them).

1. Force the current model files into your working tree (keeps your Roblox tooling):
   ```
   git fetch origin claude/roblox-animal-models-852c5h
   git checkout origin/claude/roblox-animal-models-852c5h -- models/ ROBLOX_IMPORT_PROMPT.md
   git log -1 --format=%h origin/claude/roblox-animal-models-852c5h     # must be abe6def or newer
   ```
   Then confirm the Chicken is the new one: `models/CannonTame/Animals/01_Farm/Chicken/` must contain `anims/` and
   `Chicken_Detail.png` and must NOT contain `Chicken_Texture_Studs.png`. The new Chicken has a three-point comb, block eyes
   with a thick black brow, a hanging red wattle and side wings (see `previews/Chicken_hero.png`).
2. Verify before uploading. All of these must hold, otherwise stop and tell me:
   - `models/CannonTame/Animals/<Zone>/<Name>/` exists for 77 animals (11 zones x 7), each with `<Name>.glb`, `<Name>.fbx`,
     `<Name>_Texture.png`, `<Name>_Detail.png` and an `anims/` folder.
   - `find models/CannonTame -name "*_Texture_Studs.png"` prints NOTHING (that file = old pipeline).
   - `models/CannonTame/Cannons/<NN>_<Theme>/<Theme>Cannon/` has 14 cannons; also `models/CannonTame/Shops/` and `models/CannonTame/Lobby/`.
   - Ignore `models/CannonTame/Animals/_Archive/` (replaced versions) and `models/TFFA/*Variants*`, `models/TFFA/HeadStudies/` (design studies).
3. Rebuild your upload manifest from these files only (fresh scan, not the old `game/manifest.json`), and drop every
   Cannon Tame entry from `game/asset_ids.json` / your upload cache so nothing old is reused. Re-upload them.
4. Import details (also in `models/CannonTame/Animals/README.md`):
   - Upload/import `<Name>.glb` (preferred: one file with the skinned mesh, armature and all clips) or `<Name>.fbx`.
     1 unit = 1 stud, the model faces -Z, the pivot is at the ground centre.
   - Models with glowing parts contain a separate `<Name>_Glow` mesh: set its Material to **Neon**.
   - Animations: `anims/<Name>_Idle.fbx`, `_Walk.fbx` (+ `_Fly.fbx` for winged animals; cannons have `_Idle`/`_Fire`).
     Animation Editor > Import > From FBX Animation > Loop > Publish.
   - The stud look is built into the mesh + `<Name>_Texture.png` (small recessed squares per stud cell). If you still see
     one giant square per face, you are using an old file.
5. Spot-check in Studio before laying out the showcase: `01_Farm/Chicken` should have small recessed studs all over,
   block eyes with brows, comb + wattle; `10_MythicIsles/Chimera` (lion + goat head with huge red-tipped horns + snake tail)
   and `09_Volcano/EmberWolf` (flame mane) only exist in the new set, so seeing them confirms the right files.

Note: in `08_DinoLand`, Ankylosaurus and TRex are final; Compy, Parasaurolophus, Stegosaurus, Spinosaurus and Triceratops are
being reworked - re-import those five after the next push to `claude/roblox-animal-models-852c5h`.
