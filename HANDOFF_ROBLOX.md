# Handoff prompt: move the assets into the Roblox game (step 1, the model showcase)

Paste everything below the line into a new Claude Code session on this repo.

---

We're starting to move the finished assets in this repo into the real Roblox game, "Throw Magnet for Fish". **Step 1 is only a model showcase:** get every model into my place and lay it out on the Baseplate, sorted and labelled, so I can walk around and check them all in one spot. No gameplay code yet. Read `HANDOFF.md`, `models/README.md`, `animations/README.md` and `ui/README.md` first for context, then do the steps below. Commit and push after each step.

## What goes in (140 models)
- **Fish (50):** `models/<Rarity>/<Name>/`. Rarity order: Common, Uncommon, Rare, Epic, Legendary, Mythic, Secret, Divine, Celestial.
- **Baits (15):** `models/Baits/<Rarity>/<Name>/`
- **Gym dumbbells (15):** `models/Gym/<NN>_<Theme>/<Theme>Dumbbell/`, in tier order 01 to 15
- **Zone props (60):** `models/Zones/<NN>_<Zone>/<Prop>/`, 6 per zone, zones 01 to 10
- **Skip:** `models/CannonTame/` (a different project) and `models/Gym/_Archive_Benches/`.
- Don't change anything in `models/` or `tools/blender/`. New code goes in `tools/roblox/` (Python) and `game/` (Luau and generated data).

## Step 1: manifest
Write `tools/roblox/build_manifest.py`, which scans the folders above and writes `game/manifest.json` with one entry per model:
`name`, `category` (Fish / Bait / Gym / Zone), `group` (the rarity, `NN_Theme` or `NN_Zone`), `order` (position in its group), `fbx` and `glb` paths, and `glow` (the hex colour, or null). Parse the glow colours from the tables in `models/README.md`; don't retype them. Also add the rarity colours from `ui/README.md` (the "Main" column) as a top-level `rarityColors` map. Print the count for each category; it must come to 50 / 15 / 15 / 60.

## Step 2: get the meshes into Roblox
Support both of these paths, because the place layout in step 3 must not care which one was used:

**A. Automatic upload (preferred): `tools/roblox/upload.py`**
- Upload each model's `.fbx` (the texture is embedded) as a **Model** asset with the Roblox Open Cloud Assets API (`POST https://apis.roblox.com/assets/v1/assets`, `x-api-key` header). Poll the returned operation until it's done, then record the asset ID in `game/asset_ids.json` (keyed by `name`).
- Config comes from env vars: `ROBLOX_API_KEY`, plus `ROBLOX_USER_ID` or `ROBLOX_GROUP_ID` for the creator. **Never ask me to paste the key into chat.** In a cloud session, ask for it with the secure credential form for host `apis.roblox.com` (header `x-api-key`). Tell me which Open Cloud permissions the key needs (asset read and write) and how to create one.
- Make it resumable (skip names that already have an ID), rate-limited, with `--only Name1 Name2` and `--dry-run` flags, and log failures without stopping the batch.
- **Test with 3 models before the full batch:** `Goldfish` (simple fish), `Anglerfish` (rigged, with a `_Glow` mesh) and `TreasureChest` (blocky zone prop with glow). Stop and tell me if the textures, bones or the separate `_Glow` MeshPart don't survive the upload. If FBX fails, try the `.glb`.

**B. Manual fallback:** I import the files myself with Studio's 3D Importer into a folder `ServerStorage.ShowcaseImports`, with each Model named exactly like its folder (e.g. `Goldfish`). Write me a short checklist for this in `game/README.md`.

## Step 3: the Baseplate layout (Luau)
Write `tools/roblox/gen_showcase.py`. It reads `manifest.json` and `asset_ids.json` and generates **one self-contained Luau file**, `game/ShowcaseBuilder.lua`, that I paste into the Studio **command bar** (in edit mode, so the result stays in the place). If a Roblox Studio MCP tool that runs code in Studio is connected to this session, run it yourself instead.

What the script must do:
- **Be idempotent:** delete and rebuild `Workspace.AssetShowcase` on every run. Don't touch anything else in the place, and leave the Baseplate alone.
- **Get each model** with `InsertService:LoadAsset(id)` when it has an asset ID, otherwise clone it from `ServerStorage.ShowcaseImports`. If a model is missing, place a red placeholder block with its name instead of failing, and print a summary of missing models at the end.
- **Hierarchy:** `Workspace.AssetShowcase/<Category>/<Group>/<Name>`. Give each Model these attributes: `AssetName`, `Category`, `Group`, `AssetId`, `SourcePath`.
- **Districts:** the 4 categories go side by side across the Baseplate, each on its own thin coloured floor slab with a big sign (SurfaceGui or BillboardGui text: "FISH", "BAITS", "GYM", "ZONE PROPS"). Put a `SpawnLocation` in front of them, facing the districts.
  - **Fish:** one row per rarity, in rarity order. Each row's floor strip is tinted with that rarity's colour and has a row label.
  - **Baits:** one row per rarity, same tinting.
  - **Gym:** one row of the 15 tiers in order, labelled like "07 Lava".
  - **Zone props:** one row per zone (01 to 10), 6 props each, with the zone name on a row label.
- **Spacing:** use each model's real size (`GetExtentsSize`), so big props (SubmarineWreck, StarfallWhaleShark) never overlap small ones. Leave a gap of at least 4 studs between models and at least 10 studs between rows. Sit props on the floor. Put fish and baits on a small pedestal at about chest height, turned so their side profile faces the walkway.
- **Labels:** a BillboardGui name tag above every model (name, plus a smaller rarity or zone line). Use `LuckiestGuy` or `FredokaOne` to match the UI, and set `MaxDistance` so far-away tags don't clutter the view.
- **Glow:** for every `<Name>_Glow` MeshPart, set `Material = Neon` and `Color` to the manifest colour.
- Anchor everything. Don't play animations yet.
- **Keep the default scale:** no rescaling. 1 unit = 1 stud is the size the art was made at, and checking that scale is part of the point.

## Step 4: report back
- Give me the exact steps to run it (env vars to set, commands, what to paste where).
- In `game/README.md`, list what I should check in Studio: fish scale (Commons should be about 1.6–3 studs long), fish facing (-Z), glow MeshParts separate and Neon, bones present on fish, textures showing, and any models that failed.
- Add a short "Roblox integration" status section to `HANDOFF.md`.

## Not in this step (later prompts)
Uploading the 12 animation clips and testing them, importing `ui/FishingUI.rbxmx` and filling in its image asset IDs, the stud-texture toggle, and any gameplay scripts (Rojo project setup, the magnet throw, catching and the index). Don't start these; just list anything you notice that will matter for them.
