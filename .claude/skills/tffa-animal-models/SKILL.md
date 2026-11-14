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
| `scripts/tffa_archetypes.py` | Rigged parametric builders: `quad`, `bird`, `ape`, `theropod`, `frog`, `seal`, `snake`, `scorpion`, `blob`, `golem`, `whale`, `kraken` + accessories (`horns`, `wings`, `tusks`, `mane_back`, `shell`, `plates`, `frill`, ...) and `build(name, arch, spec, out)` |
| `scripts/tffa_anim.py` | Procedural looping clips from bone names: `Idle` (always), `Walk` (legs/spine/tentacles), `Fly` (wings) |
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
   The user's standing preference: **studs on everything** (incl. dragons: `studded=True`), predators and big beasts
   **aggressive** (`snarl` or `fierce` face) and **muscular** - never "house cat", "dog with wings" or "starved".
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
7. **Rig + animate (required, every model).** Wrap parts in bone contexts: `with m.bone("Leg_FL", pivot): ...`
   (pivot = the joint: hip/shoulder for legs, neck tip for the head, chain joints for tails via `m.chain(..., bones="Tail")`).
   Use the standard names so clips are shared per family: `Body` (everything not in another bone), `Neck`, `Head`, `Jaw`,
   `Ear_L/R`, `Tail1..n`, `Leg_FL/FR/BL/BR` (quadrupeds, incl. knuckle-walking apes), `Leg_L/R` + `Arm_L/R` (bipeds),
   `Wing_L/R`, `Fin_L/R`, `Tent<k>_<j>`. Animal's left = +Y build = `_L`. `done()` builds the armature, skins every part
   rigidly to its bone, generates the clips and checks them in `previews/<Name>_anim.png` (one row per clip, top = Idle).
   Look at that strip: legs must swing in diagonal pairs, wings must flap, nothing may detach. `m.gait = {"fly": False}`
   for flightless birds, `{"hop": True}` for frogs/rabbits, `{"amp": 0.8}` to calm big animals.
8. **Batch carefully.** For rosters, build ONE zone (5-8 animals) at a time with
   `TFFA_ANIM_PREVIEW=0 /tmp/bpyenv/bin/python tools/blender/tffa_zoo.py <Zone or Names> --sheet` (each animal runs in its own
   Blender process - a whole zone in one process got OOM-killed; `TFFA_ANIM_PREVIEW=0` skips the animation strip renders,
   rigs + clips are still exported). Previews per animal: hero, front, side - check all three,
   review `<Zone>_overview.png` and `<Zone>_anim_overview.png` animal by animal, fix, rebuild, then commit and move on.
   Quality drops when many animals are generated without review - don't do it.
9. **Deliver**: `<Name>.glb` (import this into Roblox with the 3D Importer, at 1 unit = 1 stud, facing -Z, pivot at the ground centre), `<Name>.fbx`, `<Name>.blend`, `<Name>_Texture.png`, `<Name>_Detail.png` (stud shading + mutation mask), `anims/<Name>_<Clip>.fbx` (one per clip: Roblox Animation
   Editor → Import → From FBX Animation → Loop → Publish; bone names are shared, so one upload per family works for every
   animal with the same bones), and `previews/`. The GLB/FBX hold the skinned mesh + armature + all clips. Each mesh must stay under 20k triangles (the kit asserts this). Typical builds are 3-8k.

## Look options (archetype spec keys, all reviewed with the user)
| Key | Archetype | Effect | Used on |
|---|---|---|---|
| `snarl=True` | quad | open snarling jaw on a `Jaw` bone, red mouth, rows of blade teeth + long fangs, nose-bridge wrinkle, squinted eyes under steep brows (front-facing even with a long snout) | Panther |
| `fierce=True` | quad | milder aggression: narrowed eyes, pupils forward, heavy down-slanted brows, closed mouth | Mammoth |
| `muscular=True` | quad | deep chest + tucked waist + big haunches, shoulder blades, side bulges; legs = thick upper leg, lean lower leg, heavy paw with toes | Panther, Mammoth |
| `muscular=True` | dragon | barrel chest wider than the torso, pecs beside the belly shield, shoulder caps, thick arms, heavy thighs/calves, thick neck base | LavaDrake |
| `front_back=0.07` | quad | front legs tucked back under the chest (fraction of body length) | Panther |
| `tail_w=1.7` | quad | thicker `long` tail | Panther |
| `ears="cat"` | quad | short broad big-cat ears (`point`, `round`, `long`, `floppy`, `big`, `tiny`, `fennec` also exist) | Panther |
| `nostrils=True` | quad | two nostril slits instead of a nose plate | Horse |
| `head_scale=` | quad | head size (default 1.3; TFFA heads are big) | Croc 1.35, Mammoth 1.3 |
| `side_eyes=True` | quad | eyes on the head sides (long-faced animals) | Horse, Zebra, dinos |
| `gait=dict(hop=True)` / `fly=False` | quad / bird | bunny-hop walk / flightless bird (no Fly clip) | Rabbit, Ostrich, Penguin |
| `studded=True` | dragon | TFFA studs on every big dragon part | LavaDrake |
| `faceted=True` | any | no studs anywhere (only if the user asks for the smooth fantasy look) | |
| `s=` | dragon / theropod | overall scale | |

Accessories (`x=[...]`): `shaggy(col, col2)` (ice-age fur: studded hair strands, shoulder hump, domed head, cheek hair,
leg fur), `tusks("mammoth"|"walrus"|"up")`, `trunk(col)`, `jaw_teeth(n)` (croc tooth rows), `fangs(length=)`,
`horns(...)`, `wings(col, span, glow, membrane, kind="bat"|"feather")`, `mane_back`, `shell`, `plates`, `frill`, `crest`,
`sail`, `spine_spikes`, `hedgehog_spikes`, `beard`, `wool`, `mask`, `eye_patches`, `hump`, `club_tail`, `whiskers`,
`comb`, `tufts`, `bill_tip`, `ruff`, `glow_bits`, `flame_mane`, `headdress`, `astro`, `hole_ring`, `chimera_bits`,
`crescent`, `talons`, `beak_head`, `rex_cracks`.
Archetypes: `quad`, `bird`, `ape`, `theropod` (= the reviewed T-Rex), `dragon` (= the reviewed RedDragon: long neck,
horned frilled head, belly shield, spade tail, membrane wings), `frog`, `seal`, `snake`, `scorpion`, `blob`, `golem`,
`whale`, `kraken`.

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
with m.bone("Leg_FL", (x, y, hip_z)): ...                         # rig: parts inside are skinned to that bone
m.gait = {"fly": False}                                          # clip options (walk / fly / hop / amp / crawl)
m.done(views=[("hero", 40, 10, 45), ("rainbow", 50, 8, 35, "rainbow"), ("head", 35, -5, 50, "plain", (x, y, z, r))], glow_color=None)

# or a whole rigged animal from an archetype spec (design units, scaled x1.6 to studs):
from tffa_archetypes import *
build("Fox", quad, dict(body=(2.0, 0.95, 1.0), legs=(0.75, 0.32), head=(1.0, 1.05, 0.9), c1=rgb(236, 120, 40), belly=WHITE,
      snout=(0.55, 0.5, 0.4), snout_c=WHITE, ears="point", tail="bushy"), out_dir)
```
Palette constants: `WHITE BLACK PUPIL TOOTH CLAW HORN MOUTH TONGUE PINK NOSE`, helpers `dk(c, k)`, `lt(c, k)`, `mix(a, b, t)`, `hexc("#ff8800")`.
Neon parts: pass `glow=True` to a primitive. They export as `<Name>_Glow` (set Material = Neon in Roblox), and `done(glow_color=rgb(...))` sets their preview colour.
