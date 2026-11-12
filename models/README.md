# Fish models

One folder per fish: `models/<Rarity>/<FishName>/`.

| File | What it is |
|---|---|
| `<Fish>.glb` | **Import this** with the Roblox 3D Importer (texture included) |
| `<Fish>.fbx` | Backup format, texture embedded |
| `<Fish>.blend` | Blender source |
| `<Fish>_Texture.png` | Clean texture |
| `<Fish>_Texture_Studs.png` | Same texture with studs. Swap into the MeshPart `TextureID` to toggle studs. Uses `tools/blender/stud.png` as the stud tile when present |
| `previews/` | Renders, including `hero_studs` showing the studded version |

## Importing into Roblox

- Import at 1 unit = 1 stud. Fish face Roblox forward (-Z).
- Each textured mesh is under Roblox's 20k triangles-per-MeshPart limit.
- Fish with glowing parts import as a Model with two MeshParts:
  - `<Fish>`: the textured body
  - `<Fish>_Glow`: set **Material = Neon** and **Color** to the glow colour below

## Glow colours

| Fish | Glow parts | Colour |
|---|---|---|
| SeraphFish | eyes, gill slits, spiked halo | `#FFC440` (255, 196, 64) |
| ElectricEel | lightning stripes, eyes | `#78E6FF` (120, 230, 255) |
| Icefish | ice shards, eyes | `#8CE6FF` (140, 230, 255) |
| Lanternfish | photophore dots, eyes | `#78D2FF` (120, 210, 255) |
| GreenlandShark | parasite-glow eyes | `#C8FFDC` (200, 255, 220) |
| Anglerfish | lure bulb, eyes | `#B4FFC8` (180, 255, 200) |
| CrystalPike | ice cracks, eyes | `#5AE6FF` (90, 230, 255) |
| MagmaEel | lava cracks, eyes | `#FF781E` (255, 120, 30) |
| AuroraRay | aurora bands on wings | `#5AFFB4` (90, 255, 180) |
| GhostShark | ribs, spine, eyes | `#B4F0FF` (180, 240, 255) |
| EmberKoi | flame fins, whiskers, ember cracks, eyes | `#FF8C28` (255, 140, 40) |
| Megalodon | gill slits, eyes | `#FF2828` (255, 40, 40) |
| HydraEel | all six eyes | `#B4FF3C` (180, 255, 60) |
| SeaSerpent | eyes | `#5AF0FF` (90, 240, 255) |
| StarfallWhaleShark | star spots, constellation line, eyes | `#FFF0BE` (255, 240, 190) |
