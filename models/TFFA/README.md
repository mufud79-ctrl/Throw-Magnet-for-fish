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
