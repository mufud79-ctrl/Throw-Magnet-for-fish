# Prompt: import the CURRENT Cannon Tame models into Roblox

Paste everything below the line into the Roblox import/showcase session.

---

The models you imported are outdated: your branch (`claude/wonderful-gates-mxwjhe` / `claude/wizardly-lovelace-cxmaa7`) was cut
from commit `636292e`, the very first Cannon Tame prototype. Its animals use the old tiled `_Texture_Studs.png` (one big
recessed square per face + a brick pattern in Studio) and have no rig. The current models are on branch
**`claude/roblox-animal-models-852c5h`**. Use only that branch's files:

1. Get the current models (keep your Roblox tooling):
   `git fetch origin claude/roblox-animal-models-852c5h` then merge it into your branch
   (`git merge origin/claude/roblox-animal-models-852c5h`; on a conflict under `models/`, take THEIRS - that branch's file).
   Do not copy `models/` from any other branch.
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
