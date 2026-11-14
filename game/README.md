# game/: Roblox integration

Generated data and Luau for moving the repo's assets into the Roblox place "Throw Magnet for Fish".

| File | What it is | Made by |
|---|---|---|
| `manifest.json` | One entry per showcase model (140): `name`, `category`, `group`, `order`, `fbx`, `glb`, `glow`, plus `meshes`/`rigged` read from the GLB; top-level `rarityOrder` and `rarityColors` | `python3 tools/roblox/build_manifest.py` |
| `asset_ids.json` | `name` → Roblox Model asset ID | `tools/roblox/upload.py` |
| `upload_failures.json` | Models whose last upload failed, with the error | `tools/roblox/upload.py` |
| `ShowcaseBuilder.lua` | Command-bar script that builds `Workspace.AssetShowcase` | `python3 tools/roblox/gen_showcase.py` |

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
export ROBLOX_API_KEY=...        # or let the Claude cloud session inject it (secure form)
export ROBLOX_USER_ID=123456     # your user ID (number in your profile URL), or:
# export ROBLOX_GROUP_ID=7890    # if the place is group-owned
python3 tools/roblox/build_manifest.py
python3 tools/roblox/upload.py --only Goldfish Anglerfish TreasureChest   # test 3 first
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
