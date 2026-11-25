# Roblox runtime

`templates/` is a Rojo project (`default.project.json`); without Rojo, recreate the same tree in Studio:
- ReplicatedStorage/AnimeVFX (ModuleScript = init.lua) with children Assets (ModuleScript) and Effects
  (Folder of ModuleScripts, one per move)
- ServerScriptService/AnimeVFXServer (Script) - creates `AnimeVFXEvent` + demo `AnimeVFXRequest`, validates,
  broadcasts
- StarterPlayerScripts/AnimeVFXClient (LocalScript) - plays broadcasts; AnimeVFXDemo (Q/E pick, F cast)

## Assets
1. `assets/upload_manifest.json` lists exactly the PNGs (116) and FBX meshes (16) the moves use.
2. Upload (Asset Manager bulk import / Creator Dashboard). Uploads are public-facing and moderated: the user does
   this, in one batch, after approving the set.
3. Paste ids into `Assets.lua` (TEXTURES / MESHES). Until then textures fall back to a built-in sparkle and
   meshes are invisible, so moves still run.
4. Mesh calibration: kit meshes fit a 2-stud box. Insert one as a MeshPart and check MeshSize; if it isn't ~2
   studs, set `MESH_SCALE[name]` so SpecialMesh.Scale 1 = 2 studs.

## Rig models (skinned)
Rigged creatures (e.g. `thunder_serpent`) can't be built from a MeshId at runtime. Import the FBX listed under
`rig_models` in the upload manifest with the 3D Importer (keep the rig/bones), name the MeshPart (or Model) after the
spec's `model`, and put it in `ReplicatedStorage/AnimeVFX/Models`. The runtime clones it per cast and sets each
Bone.WorldCFrame every frame. Check the import scale: the serpent is authored 18 studs long.

## Playing
```lua
local AnimeVFX = require(game.ReplicatedStorage.AnimeVFX)
local handle = AnimeVFX.Play("000_FireFist", AnimeVFX.CastFrame(character), {
	caster = character, targets = { enemy },
	onHit = function(i, t) --[[ hit-reaction animation / knockback here ]] end,
})
```
Server: validate the move, then `AnimeVFXEvent:FireAllClients(name, castFrame, caster, targets)`.
Gameplay (damage, hitboxes) runs on the server on its own timeline; never wait on an effect.

## How each spec feature maps
Emitters -> Attachments on an anchored root part (moving attachments are updated every frame); shape emission
-> a sized invisible Part. Shells -> Part + SpecialMesh (FileMesh), Scale/CFrame/Transparency driven per frame;
Textured shells use SmoothPlastic + TextureId + VertexColor (Transparency min 0.02). Beams -> two Attachments.
Bolts -> thin Neon parts rebuilt every flicker. Debris -> anchored parts on computed paths, material and colour
raycast from the ground. Lights -> PointLight. Numbers -> BillboardGui. Ghosts -> Neon clones of the caster's
parts. Grade -> one ColorCorrectionEffect. Impact frames -> ColorCorrection + Highlights (Roblox can't invert
the screen: "invert" = white world + black silhouettes, "mono" = the reverse). Hit-stop -> emitter TimeScale 0
+ AnimationTrack:AdjustSpeed(0).

## Performance
Burst counts and rates scale with `AnimeVFX.Quality` x the player's graphics level (0.3-1). Keep a move under
~40 emitters live at once on mobile; stacks cost 3-4 emitters each, so prefer fewer, bigger stacks. Highlights
are capped at 31 at a time.

## Not verified here
The Luau was parsed for structure (luaparse) but has not been run inside Roblox Studio from this environment.
First Studio run: check the console, calibrate mesh scale, and confirm ForceField material on SpecialMesh shells
looks right on your target devices.
