# Fish models

One folder per fish: `models/<Rarity>/<FishName>/`.

| File | What it is |
|---|---|
| `<Fish>.glb` | **Import this** with the Roblox 3D Importer (texture included) |
| `<Fish>.fbx` | Backup format, texture embedded |
| `<Fish>.blend` | Blender source |
| `<Fish>_Texture.png` | Clean texture |
| `<Fish>_Texture_Studs.png` | Same texture with classic Roblox studs; swap it into the MeshPart's `TextureID` to add studs |
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
| SeraphFish | halo, forehead gem, star dots | `#FFC850` (255, 200, 80) |
