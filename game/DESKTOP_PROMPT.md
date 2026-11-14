# Desktop prompt: upload the models and build the showcase in Studio

**Before you paste it:**
1. Create the Open Cloud API key (`game/README.md` → "Create the API key": Assets **Read + Write**,
   your IP or `0.0.0.0/0`, short expiry).
2. In your local clone of the repo, create a file named `.env` in the repo root (it's git-ignored) with:
   ```
   ROBLOX_API_KEY=paste-the-key-here
   ROBLOX_USER_ID=your-numeric-user-id
   ```
   Use `ROBLOX_GROUP_ID=...` instead of `ROBLOX_USER_ID` if the place is owned by a group.
3. Open the place in Roblox Studio (edit mode). If you use the Roblox Studio MCP, make sure it's connected.

Then paste everything below the line into a Claude Code session on your desktop, opened on this repo.

---

We're on step 1 of moving this repo's assets into my Roblox game: a **model showcase** on the Baseplate.
The code is already written on branch `claude/wonderful-gates-mxwjhe`. Your job is to run it, check the result and fix what breaks.
Read `game/README.md` first (instructions plus the Studio checklist), then the "Roblox integration" section at the end of `HANDOFF.md`.

**Setup**
- `git fetch origin claude/wonderful-gates-mxwjhe && git checkout claude/wonderful-gates-mxwjhe && git pull`. Work and push on this branch.
- My API key is in the git-ignored `.env` at the repo root, and `tools/roblox/upload.py` reads it.
  **Never print, echo, cat or commit `.env` or the key**, and never ask me to paste the key into chat.
  To check it's set up, run `python3 tools/roblox/upload.py --dry-run --only Goldfish`; only a real run uses the key.
- Check whether a Roblox Studio MCP tool that runs Luau in Studio is available (e.g. `run_code`). If it is, run the
  generated `.lua` files through it yourself (in edit mode, so the result stays in the place). If it isn't, tell me
  each time exactly which file to paste into the Studio command bar, and wait for me to paste back the Output.

**1. Test upload (3 models)**
- `python3 tools/roblox/build_manifest.py` (must print 50 / 15 / 15 / 60).
- `python3 tools/roblox/upload.py --only Goldfish Anglerfish TreasureChest`
- `python3 tools/roblox/gen_showcase.py`, then run `game/CheckUploads.lua` in Studio.
- Expected: Goldfish has a textured MeshPart and Bones; Anglerfish has Bones plus a separate `Anglerfish_Glow` MeshPart;
  TreasureChest has a textured MeshPart plus `TreasureChest_Glow`. **If textures, bones or the separate `_Glow` MeshPart
  are lost, stop and tell me.** First try the `.glb` (`upload.py --format glb --force --only <name>`) and say which format kept what.
- If the upload API itself fails, fix `tools/roblox/upload.py`: it was written from the Open Cloud Assets API docs but has
  never been run against the real API. Show me the error with the key redacted.
- Commit `game/asset_ids.json` and any fixes, then push.

**2. Full batch**
- `python3 tools/roblox/upload.py` (resumes and skips what's done). Use `--glb-fallback` if the test showed FBX sometimes fails.
- Retry the failures in `game/upload_failures.json` once; report any that still fail.
- `python3 tools/roblox/gen_showcase.py`, then run `game/CheckUploads.lua` again and summarise any problems per model.
- Commit and push.

**3. Build the showcase**
- Run `game/ShowcaseBuilder.lua` in Studio (edit mode). It rebuilds `Workspace.AssetShowcase` and touches nothing else.
- With the MCP, inspect the result yourself: missing or red-placeholder models, `_Glow` parts that aren't Neon,
  Common fish lengths (expected about 1.6–3.1 studs), and any overlapping models in a row (compare bounding boxes).
- The script has only been syntax-reviewed by hand, never run. If it errors, fix `tools/roblox/showcase_template.lua`
  (not the generated file), regenerate, and run it again.
- Then ask me to walk it and save the place. Give me the `game/README.md` checklist, filled in with what you could verify.

**Rules**
- Don't change `models/` or `tools/blender/`. Known issue: SunkenContainer has a glow colour in `models/README.md` but no `_Glow` mesh. Just report it.
- Keep the default scale (no rescaling) and don't play animations.
- Don't start the later steps (animation clips, UI import, stud toggle, gameplay or Rojo).
- At the end, update the "Roblox integration" section of `HANDOFF.md` (what's uploaded, what passed, what failed), then commit and push.
