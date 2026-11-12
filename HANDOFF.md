# Handoff prompt: fish models for "Throw Magnet for Fish" (Roblox)

Paste everything below the line into a new Claude Code session on this repo.

---

You're continuing a batch of stylised fish models for a Roblox fishing game. I only want models, no game code.
Develop on branch `claude/blender-model-creation-rl2cys`. Commit and push after each batch.

## Status
Done (in `models/<Rarity>/<Name>/`):
- **Divine:** DragonKoi (the style reference I love, don't change it), SeraphFish (aggressive shark-style angel)
- **Common (10):** Minnow, Goldfish, Bluegill, Guppy, Perch, Carp, Catfish, Sardine, Clownfish, BlueTang
- **Uncommon (9):** Koi, LargemouthBass, RainbowTrout, Salmon, Mudskipper, Pufferfish, Angelfish, Flounder, Seahorse
- **Rare (8):** Pike, Sturgeon, Piranha, ElectricEel, Lionfish, MorayEel, Icefish, Lanternfish (`rares.py`; template for aggressive spec fish: `jaw`, `brow`, slit `pupil`, `eye_k`, `glow_eyes`, `dots`, `glow_line`, `wiggle`)
- **Epic (7):** AlligatorGar, Arapaima, MantaRay, HammerheadShark, GreenlandShark, Anglerfish, Blobfish (`epics.py`: custom hooks for hammer head, manta wings, angler lure)
- **Legendary (6):** GreatWhiteShark, Sailfish, CrystalPike, Oarfish, MagmaEel, Coelacanth (`legendaries.py`: `cracks()` glowing crack lines, `gills()`)
- **Mythic (4):** AuroraRay, GhostShark, EmberKoi, GoldenArowana; **Secret (3):** Megalodon, HydraEel, SeaSerpent; **Celestial (1):** StarfallWhaleShark (`top_tiers.py`)

**All 50 fish are built.** Possible follow-ups if the user asks:
- Polish passes on individual fish (render a `front` view by passing `views=` in the spec; dramatic fish sell on their front silhouette).
- EmberKoi body reads thin; the HydraEel's second neck is hidden in the 3/4 view.
- Variants (Gold/Shiny/Giant) as texture or colour swaps.
- Testing the imports in Roblox Studio (not done yet: confirm scale, facing and that Glow meshes import as separate MeshParts).

## Style rules (already approved)
- **Look:** stylised cartoon with smooth shading and readable chunky silhouettes. Big expressive eyes (an iris sphere, a pupil and a glint). Painted texture detail: scales, patterns, and fin rays that fade toward pale tips. Slight swim curve in the tail.
- **Rarity shows through design:** Commons are plain natural fish, about 1.6–3 studs long. Rarer fish get more parts and more drama, up to about 6–7 studs.
- **Rare fish and up must be aggressive and cool**, not cute. Compare a 1998 Mazda with an M5 Competition. Sharp, swept-back shapes. The front silhouette matters, so render a front view for dramatic fish. Shark-like menace beats "sardine". Be creative with shapes and meshes; don't just reuse one body.
- **Glow, only where it fits** (lures, lava cracks, photophores, auras): put it in a separate `<Name>_Glow` mesh (`glow=True` on parts), one colour per fish, and add a row to `models/README.md`'s glow table.
- **Budget:** under 20k triangles per mesh (the Roblox limit). Commons run about 7k.
- **Studs:** every fish gets `<Name>_Texture_Studs.png` automatically, made from `tools/blender/stud.png` (a 4×4 tile). The default cell is 0.15 studs, which the user approved.

## Tooling (Blender 5.3 as a Python module)
- Setup if the venv is missing: `python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy` (Python 3.13 wheel, about 430 MB). Run scripts with `/tmp/bpyenv/bin/python`.
- `tools/blender/fishkit.py` is the core kit. `Fish` is a lofted body with helpers `fin`, `tube` (`rfn=` for a radius profile), `sphere`, `torus`, `gem` and `eyes`. It also has `texture` (a 1024 atlas: top half body, then fin gradients, gradient strips and swatches), `finish` (join, bend, `roll`, export GLB/FBX/.blend, previews) and `contact_sheet`.
- `tools/blender/fishgen.py` is the spec-dict builder `build(sp)`. Optional keys include `rarity`, `hook` (a custom-geometry callback), `extra` (a custom texture painter), patterns (`bars`, `stripe`, `spots`, `speckle`, `bands`, `spot`), `barbels`, `roll`, `bend`, `cam`, `glow`, `eyes=False`, `pect=0` and `pelv=0`.
- Batch scripts: `commons.py`, `uncommons.py` (see its Seahorse for a fully custom build and its Flounder for a roll plus hook). Bespoke scripts: `dragon_koi.py`, `seraph_fish.py` (open jaw, teeth, blade wings and glow parts: a good template for aggressive fish).
- Pattern: create `rares.py`, `epics.py` and so on, one per rarity. Run `python rares.py [Name ...]`. Then build one `contact_sheet` of the `_hero.png` renders (`step=4`) and review that single image instead of every render.

## Workflow / token rules
- Keep token use low. Write each batch in one pass, review only the contact sheet, and do at most one fix round per batch.
- Delete `*.blend1` before committing.
- After each batch, update this file's Status section, commit and push.
