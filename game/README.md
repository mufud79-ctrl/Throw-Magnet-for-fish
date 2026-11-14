# game/: Roblox integration

Generated data and Luau for moving the repo's assets into the Roblox place "Throw Magnet for Fish".

| File | What it is | Made by |
|---|---|---|
| `manifest.json` | One entry per showcase model (140): `name`, `category`, `group`, `order`, `fbx`, `glb`, `glow`, plus `meshes`/`rigged` read from the GLB; top-level `rarityOrder` and `rarityColors` | `python3 tools/roblox/build_manifest.py` |
| `asset_ids.json` | `name` → Roblox Model asset ID | `tools/roblox/upload.py` |
| `upload_failures.json` | Models whose last upload failed, with the error | `tools/roblox/upload.py` |
| `ShowcaseBuilder.lua` | Command-bar script that builds `Workspace.AssetShowcase` | `python3 tools/roblox/gen_showcase.py` |
| `CheckUploads.lua` | Command-bar script that loads each uploaded asset (without adding it) and reports MeshParts, textures, Bones and the `_Glow` part | `python3 tools/roblox/gen_showcase.py` |
| `DESKTOP_PROMPT.md` | Prompt for a Claude Code session on your desktop that does the upload and the Studio build | n/a |

## Path A: automatic upload (Open Cloud)

### Create the API key
1. Go to <https://create.roblox.com/dashboard/credentials> and choose **Create API Key**.
   If your place belongs to a group, switch the dashboard to that group first so the group owns the key and the assets.
2. Under **Access Permissions**, add the **Assets** API system and tick **Read** and **Write**
   (scopes `asset:read` and `asset:write`). Optional, for `upload.py --inspect`: also add
   **Legacy Assets** (asset delivery), operation **Manage**.
3. Under **Security**, add the IP addresses allowed to use it. For a cloud session, `0.0.0.0/0` is
   the practical choice; give the key a short expiration, and delete it when the upload is finished.
4. Save and copy the key. Keep it out of chat, commits and files in this repo.

### Run it
```bash
export ROBLOX_API_KEY=...        # or put the ROBLOX_* lines in a .env file at the repo root (git-ignored)
export ROBLOX_USER_ID=123456     # your user ID (number in your profile URL), or:
# export ROBLOX_GROUP_ID=7890    # if the place is group-owned
python3 tools/roblox/build_manifest.py
python3 tools/roblox/upload.py --only Goldfish Anglerfish TreasureChest   # test 3 first
python3 tools/roblox/gen_showcase.py     # bakes the IDs into CheckUploads.lua / ShowcaseBuilder.lua
#   -> paste game/CheckUploads.lua into the Studio command bar and read the Output
python3 tools/roblox/upload.py                                             # then the rest (resumes)
python3 tools/roblox/upload.py --format glb --only <names that failed>     # retry with .glb
```
The assets must be owned by the same user or group that owns the place, otherwise
`InsertService:LoadAsset` refuses them in Studio.

## Path B: manual import (fallback)

Use this for any model that has no ID in `asset_ids.json`; the builder falls back to it automatically.

1. In the Explorer, under **ServerStorage**, insert a **Folder** named exactly `ShowcaseImports`.
2. **File → Import 3D** (3D Importer), pick a model's `.glb` (or `.fbx`) from `models/...`
   (paths are in `manifest.json`). You can select several files at once.
3. In the importer: keep **Scale** at 1 (no rescale, "1 unit = 1 stud"), leave **Rig** on for fish,
   leave **Anchored** either way (the builder anchors everything), then **Import**.
4. Drag each imported Model into `ServerStorage.ShowcaseImports`.
5. Make sure each Model's name is **exactly** the folder name (e.g. `Goldfish`, `TreasureChest`,
   `LavaDumbbell`); the importer sometimes adds suffixes. Names are case-sensitive.
6. Check that glowing models contain both MeshParts, `<Name>` and `<Name>_Glow`.
7. Run `game/ShowcaseBuilder.lua` (below). Anything still missing shows as a red block and is listed in the Output.

Mixing is fine: models with an asset ID are loaded, the rest are cloned from `ShowcaseImports`.

## Building the showcase

1. `python3 tools/roblox/gen_showcase.py` (after any upload, so the IDs are baked in).
2. Open the place in Studio, **edit mode** (not Play). Open **View → Command Bar** and **View → Output**.
3. Open `game/ShowcaseBuilder.lua`, copy **all** of it, paste it into the command bar and press Enter.
   It takes a little while (one `LoadAsset` per model) and prints progress, then a summary.
   With the Roblox Studio MCP connected, a Claude session can run the file's contents itself instead.
4. **Save the place** (File → Save to Roblox). Re-running replaces `Workspace.AssetShowcase` and nothing else.

What it builds: `Workspace.AssetShowcase/<Category>/<Group>/<Name>` (each Model has the attributes
`AssetName`, `Category`, `Group`, `AssetId`, `SourcePath`), plus `AssetShowcase/_Layout` with the floors,
signs, row strips, pedestals, name tags and a `ShowcaseSpawn` SpawnLocation. Four districts side by side
(FISH, BAITS, GYM, ZONE PROPS), entrances facing the spawn; rows run away from you. About 363 × 250 studs, starting 30 studs behind the origin.

The place's original SpawnLocation is left alone. If you spawn there instead of on `ShowcaseSpawn`,
turn off its `Enabled` property while you test, or just walk forward: the showcase is in front of it.

## What to check in Studio

- [ ] Output summary: `0 missing` and no `expected a _Glow MeshPart` warning (except SunkenContainer, below).
- [ ] **Scale, no rescaling:** Common fish are about 1.6–3 studs long (Clownfish 1.6, Goldfish 2.1, Catfish 3.1);
      the biggest are StarfallWhaleShark (~8 long) and MangroveRoots (~10 × 12 × 10). Compare against your avatar.
- [ ] **Facing:** the showcase turns fish and baits -90°, so if the import kept "forward = -Z", every fish's head
      points **right** (+X) as you face the rows. A fish whose head points left or at you was imported with a different forward axis.
- [ ] **Glow:** glowing models have a **separate** `<Name>_Glow` MeshPart, now Neon in its manifest colour
      (Anglerfish lure, TreasureChest gold, all of StarfallLake, and so on).
- [ ] **Bones:** fish MeshParts contain `Bone` instances (Root, Head, Jaw, Spine1–4, Tail, Pect_L/R). Without them the shared animation clips won't work later.
- [ ] **Textures:** every model shows its painted texture (not grey). The `_Glow` parts are untextured by design.
- [ ] Failed models: anything listed in `game/upload_failures.json` or shown as a red placeholder block.

Known before testing: `models/README.md` lists a glow colour for **SunkenContainer**, but the model has no
`_Glow` mesh (its builder in `zones_blocky.py` makes no glow parts). It will show up in the
"expected a _Glow MeshPart" warning. Either the README row or the model needs fixing later.

## Notes for the later steps

- **Animations:** `game/manifest.json` marks all 50 fish `rigged`. The importer adds an `AnimationController`
  only sometimes; the gameplay code should add `AnimationController` + `Animator` if missing. The showcase anchors
  everything, which is fine for skinned meshes (bones still animate on anchored parts).
- **Glow parts and bones:** confirm the `_Glow` MeshPart is skinned to the same bones (animations/README.md flags this as untested); otherwise the glow will stay put while the body swims.
- **Stud texture toggle:** each model has `<Name>_Texture_Studs.png`; those PNGs must be uploaded as Decal/Image
  assets and swapped into `MeshPart.TextureID` (or a SurfaceAppearance). Open Cloud uploads them the same way (`assetType: Decal`).
- **UI:** `ui/FishingUI.rbxmx` image IDs can be filled by the same uploader pattern (Decal assets) plus a command-bar
  pass over the `AssetFile` attributes; `ui/asset_map.json` already lists the mapping.
- **Rojo / gameplay:** the showcase lives in Workspace and is generated, so keep it out of a Rojo project tree.
  Gameplay code can find models by the `AssetName`/`Category` attributes, or better, by asset ID from `asset_ids.json`
  (load into ReplicatedStorage at runtime) rather than from the showcase.
