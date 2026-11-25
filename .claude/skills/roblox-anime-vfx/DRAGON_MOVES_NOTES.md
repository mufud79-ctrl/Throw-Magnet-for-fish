# Dragon fruit (hybrid + full form): working notes (branch claude/dragon-fruit-vfx-k354ta)

Brief: `prompts/dragon_fruit_session.md`. Design: `lab/dragon/DESIGN.md`.

## Layout
- `lab/dragon/kit.py`       per-fruit kit (fire palette, layer conventions, helpers), from `lab/thunder/kit.py`
- `lab/dragon/moves/*.py`   one script per move -> `dragon_NN_Name.json`
- `assets/renders/dragon/`  MP4s + strips shown to the user
- Export (after all approved): `python3 scripts/export_luau.py --effects lab/dragon/moves`

## Status
| step | status |
|---|---|
| 1. research + design doc | shown, waiting for approval |
| 2. concept sheet | - |
| 3. Meshy model + rig (wings) + rig layer v2 | - |
| 4. fire matter | - |
| 5. hybrid Z X C V B F | - |
| 6. full form Z X C V B F | - |
| 7. second pass | - |
| 8. export + manifest | - |

## Step 1: research
~60 videos' auto-frames (vfx-reference-frames). Takeaways in DESIGN.md section 1. Key: Type Soul fire on sand =
saturated gold body + crimson rim (no white-out), crescents with torn tongues; black smoke is the dark anchor of
every fire blast; dark dragons with lava seams read best; breath needs rolling billows + ember spray + ground
splash/scorch, never a clean cylinder; tornado = spiral bands.

## Credits
| item | estimate | spent |
|---|---|---|
| Figma concept image | 1-2 images | - |
| Meshy multi-image-to-3D | 30 (cap 60) | - |
