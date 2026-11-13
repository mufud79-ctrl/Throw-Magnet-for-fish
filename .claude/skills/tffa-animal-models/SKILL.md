---
name: tffa-animal-models
description: Build Roblox animal/creature 3D models in the exact "Throw Food For Animals" (TFFA) style - chunky chamfered faceted blocks, recessed-square stud texture, block eyes with thick brows, white blade teeth - as importable GLB/FBX with a texture atlas, plus previews and a harsh side-by-side review against a reference. Use whenever the user asks for a TFFA-style / Throw Food For Animals-style animal, pet, creature, dinosaur, monster or bird model, wants more animals "in that style", or wants an existing one compared to a reference and improved.
---

# TFFA-style animal models

Everything needed is in this folder:

| Path | What |
|---|---|
| `scripts/tffa_kit.py` | The builder. `Model` + primitives (`box`, `hexa`, `seg`, `chain`, `spike`, `slab`, `poly`, `ball`), the face kit (`eyes`, `teeth`), `frame()` groups, atlas + export |
| `scripts/tffa_render.py` | Previews: Roblox-like light, ground shadow, thick black thumbnail outline, `rainbow` mutation preview |
| `scripts/compare.py` | Reference vs ours side-by-side sheet (system `python3` + Pillow) |
| `references/style_guide.md` | **Read first.** The style rules, measured from the real game shots |
| `references/review_checklist.md` | The harsh comparison checklist + known pitfalls and their fixes |
| `references/ref_images/` | Real in-game references (gorilla, T-Rex icon, red dragon, phoenix, pumpkin spider, carrot) |
| `examples/` | Finished, reviewed builds: `gorilla.py` (studded, front eyes, rainbow), `trex.py` (studded, open jaw, side eyes), `dragon.py` (faceted fantasy, wings), `phoenix.py` (gradient feathers) |

## Setup (once per container)
```bash
[ -x /tmp/bpyenv/bin/python ] || (python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install -q bpy numpy)
```
`bpy` is Blender as a Python module (~430 MB, about 1 min). `compare.py` uses the system `python3` with Pillow.

## Workflow
1. **Pin the reference.** Use a real in-game shot (a user image, a thumbnail, `references/ref_images/`). Fan art (voxel/Minecraft-like AI images) is NOT the style - ignore it. Note: silhouette, proportions (head size!), colours, face, signature parts.
2. **Pick the tier look** (style_guide §1): *studded* (common/natural animals) or *faceted* (rare/fantasy: no studs, gradients allowed).
3. **Copy the closest example** to `examples/<animal>.py` and edit. Build in studs: +X forward, +Y = animal's left, +Z up, ground at z = 0. Mirror with `for s in (1, -1)`.
4. **Build + render** (about 1-2 min per model):
   ```bash
   cd .claude/skills/tffa-animal-models
   TFFA_SAMPLES=24 /tmp/bpyenv/bin/python examples/<animal>.py [out_dir] [--no-render]
   ```
   Default output: `<repo>/models/TFFA/<Name>/`. Previews land in `<out>/previews/`.
5. **Compare harshly.** Render a view that matches the reference camera (`views` tuple: azimuth 0 = face, +90 = animal's left side; az +40..60 puts the face on the LEFT of the image; add a close-up focus `(x, y, z, radius)` for head shots). Then:
   ```bash
   python3 scripts/compare.py /tmp/cmp.png REF.png[:x0,y0,x1,y1] <out>/previews/<Name>_<view>.png
   ```
   Open the sheet and go through `references/review_checklist.md` point by point. Write down every difference, worst first (silhouette > proportions > face > colour > detail).
6. **Fix and repeat** until a fresh look finds nothing silhouette/proportion/face-level. Typically 3-6 rounds. Do not stop at "looks okay". Check the front and side views too, not only the matching view (thin edge-on wings and hidden eyes show up there).
7. **Deliver**: `<Name>.glb` (import this into Roblox with the 3D Importer, at 1 unit = 1 stud, facing -Z, pivot at the ground centre), `<Name>.fbx`, `<Name>.blend`, `<Name>_Texture.png`, `<Name>_Detail.png` (stud shading + mutation mask), and `previews/`. Each mesh must stay under 20k triangles (the kit asserts this). Typical builds are 3-8k.

## Kit cheat-sheet (all sizes in studs, colours from `rgb(r, g, b)`)
```python
from tffa_kit import *
m = Model("Fox", out_dir_or_None, stud=0.6, chamfer=0.18, jitter=0.05)  # stud = world size of one stud cell
m.box(name, center, (L, W, H), COL, rot=Ry(a), top=(sx, sy), bot=(sx, sy), shift=(dx, dy), studs=True|'top'|False)
m.hexa(name, [8 corners: bottom -x-y,+x-y,+x+y,-x+y then top], COL)      # exact silhouettes (backs, wedges)
m.seg(name, a, b, w0, w1, COL, d0=, d1=)       # tapered limb/neck block from a to b
m.chain(name, [p0, p1, ...], [w0, w1, ...], COL)  # stepped tails, trunks, tentacles
m.spike(name, base, tip, r, COL, flat=0.3)     # teeth/claws/horns; flat<1 = blade wide along X
m.slab(name, [(x, y) outline], thick, COL, origin=, xaxis=, yaxis=, grad=(c0, c1[, c2]))  # ears, feathers, leaves
m.poly(name, [3D points], thick, COL)           # wing membranes / big fins through arbitrary 3D points
m.ball(name, center, r, COL)                    # low-poly faceted ball (knobs, berries)
m.eyes(left_eye_center, facing=(1,0,0), size=(w, h), pupil=0.6, look=(toward_nose, up), angry=0.3, ...)
m.teeth(name, start, end, n, length, r)
with m.frame(pivot=, scale=1.25, rot=Ry(a), move=(0,0,1)): ...   # resize a head, open a jaw, pose a limb
m.done(views=[("hero", 40, 10, 45), ("rainbow", 50, 8, 35, "rainbow"), ("head", 35, -5, 50, "plain", (x, y, z, r))], glow_color=None)
```
Palette constants: `WHITE BLACK PUPIL TOOTH CLAW HORN MOUTH TONGUE PINK NOSE`, helpers `dk(c, k)`, `lt(c, k)`, `mix(a, b, t)`, `hexc("#ff8800")`.
Neon parts: pass `glow=True` to a primitive. They export as `<Name>_Glow` (set Material = Neon in Roblox), and `done(glow_color=rgb(...))` sets their preview colour.
