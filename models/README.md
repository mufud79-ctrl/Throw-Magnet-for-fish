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
