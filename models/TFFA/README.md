# TFFA-style animals ("Throw Food For Animals" look)

Built with the skill in `.claude/skills/tffa-animal-models/` (read its `SKILL.md`). `TFFA_vs_reference.png` shows each model next to the real game shot it was tuned against.

| Model | Look | Reference |
|---|---|---|
| Gorilla | studded, angry block eyes, rainbow-mutation preview | in-game rainbow gorilla |
| TRex | studded gold, open jaw, white blade teeth | game icon |
| RedDragon | faceted fantasy, raised wings, lilac belly shield | in-game red dragon |
| Phoenix | faceted, 3-stop gradient feathers, tail gems | in-game phoenix |
| Cow | studded quadruped template | (style only) |

Each folder holds `<Name>.glb` (import this with the Roblox 3D Importer at 1 unit = 1 stud; it faces -Z, pivot at the ground centre), `.fbx`, `.blend`, `<Name>_Texture.png`, `<Name>_Detail.png` (stud shading 0.5 = flat, alpha 0 = colours a mutation must keep) and `previews/`.
Rebuild: `cd .claude/skills/tffa-animal-models && /tmp/bpyenv/bin/python examples/<animal>.py`.

## Design studies (user feedback rounds)
| Folder | What | User pick |
|---|---|---|
| `HeadStudies/` | 4 lion heads + 4 horse heads on neck stubs (`tools/blender/tffa_head_studies.py`) | L2 lion, H1 horse (now head kits `lion_sunburst`, `horse_wedge`) |
| `SpaceVariants/` | 4 MoonBunny + 4 SpaceCat full-body concepts (`tools/blender/tffa_space_variants.py`) | BunnyC_Saturn, CatC_Alien |
| `SalamanderVariants/` | 4 FireSalamander concepts (`tools/blender/tffa_salamander_variants.py`) | SalB_MagmaNewt |

The full Cannon Tame roster lives in `models/CannonTame/Animals/` (see its README).

