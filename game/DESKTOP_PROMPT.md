# Desktop prompt: get the models into Studio and build the showcase

**Before you paste it:** open the place in Roblox Studio (edit mode).

Then paste everything below the line into a Claude Code session on your desktop, opened on this repo.

---

We're on step 1 of moving this repo's assets into my Roblox game: a **model showcase** on the Baseplate.
The code is already written on branch `claude/wonderful-gates-mxwjhe`. Your job is to get the models into Studio,
run the showcase, check it and fix what breaks. Use the Roblox Studio connection you have to run code and inspect the place.
Read `game/README.md` first (Path B, "Building the showcase" and the Studio checklist), then the "Roblox integration" section at the end of `HANDOFF.md`.

**Setup**
- `git fetch origin claude/wonderful-gates-mxwjhe && git checkout claude/wonderful-gates-mxwjhe && git pull`. Work and push on this branch.
- `python3 tools/roblox/build_manifest.py` (must print 50 / 15 / 15 / 60), then `python3 tools/roblox/gen_showcase.py`.

**1. Get the meshes in: test 3 models first**
- Target: `ServerStorage.ShowcaseImports` (a Folder) holding one Model per asset, named **exactly** like its folder
  (e.g. `Goldfish`). `game/manifest.json` lists every model with its `.glb`/`.fbx` path. Keep scale 1 (no rescaling) and keep the rig.
- Import `Goldfish`, `Anglerfish` and `TreasureChest` (paths in the manifest) into that folder, whichever way works best from your setup.
- Run `game/CheckUploads.lua` in Studio. It reads `ShowcaseImports` for models without an asset ID.
  Expected: Goldfish has a textured MeshPart and Bones; Anglerfish has Bones plus a separate `Anglerfish_Glow` MeshPart;
  TreasureChest has a textured MeshPart plus `TreasureChest_Glow`.
  **If textures, bones or the separate `_Glow` MeshPart are lost, stop and tell me.** Try the other format (`.fbx` vs `.glb`) and say which kept what.

**2. All 140**
- Import the rest the same way, then fix names (strip importer suffixes) and move the Models into `ShowcaseImports`.
- Run `game/CheckUploads.lua` again. It lists anything still missing and any per-model problems. Summarise them.

**3. Build the showcase**
- Run `game/ShowcaseBuilder.lua` in Studio, in edit mode. It rebuilds `Workspace.AssetShowcase` and touches nothing else.
- Inspect the result: red placeholders, `_Glow` parts that aren't Neon, Common fish lengths (expected about 1.6–3.1 studs),
  fish heads pointing +X, and overlapping models in a row (compare bounding boxes).
- The Luau has only been reviewed by hand, never run. If it errors, fix the template (`tools/roblox/showcase_template.lua` or
  `check_template.lua`), not the generated file, run `gen_showcase.py` and try again.
- Then ask me to walk it and save the place. Give me the `game/README.md` checklist, filled in with what you could verify.

**Rules**
- Don't change `models/` or `tools/blender/`. Known issue: SunkenContainer has a glow colour in `models/README.md` but no `_Glow` mesh. Just report it.
- Keep the default scale (no rescaling) and don't play animations.
- Don't start the later steps (animation clips, UI import, stud toggle, gameplay or Rojo).
- At the end, update the "Roblox integration" section of `HANDOFF.md` (how the models got in, what passed, what failed). Commit and push after each step.
