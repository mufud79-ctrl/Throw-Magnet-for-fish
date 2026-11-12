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

Still to build (29). Rarity, then name, then water area, then design notes:
- **Rare:** Pike (river: long duck-bill snout, toothy), Sturgeon (river: bony back plates, shovel snout, barbels), Piranha (swamp: deep body, underbite with teeth, red belly), ElectricEel (swamp: long eel with **glowing stripes**), Lionfish (reef: fan of striped venom spines), MorayEel (reef: eel with open toothy mouth, spotted), Icefish (frozen sea: see-through pale body, **glowing** blood-line optional), Lanternfish (abyss: small, rows of **glowing** photophores)
- **Epic:** AlligatorGar (swamp: gator snout, armour scales), Arapaima (swamp: huge, red-scaled tail half), MantaRay (reef: wide wings, head fins), HammerheadShark (open ocean), GreenlandShark (frozen sea: slow grey, scarred), Anglerfish (abyss: **glowing lure**, huge fanged mouth), Blobfish (abyss: droopy comic blob)
- **Legendary:** GreatWhiteShark (open ocean), Sailfish (open ocean: huge sail fin, bill), CrystalPike (frozen sea: pike made of ice crystal facets, **glowing** cyan core), Oarfish (abyss: very long ribbon, red crest), MagmaEel (volcanic vent: rocky crust with **glowing lava cracks**), Coelacanth (sunken ruins: ancient, lobed fins)
- **Mythic:** AuroraRay (frozen sea: ray with **glowing** aurora bands), GhostShark (abyss: see-through, **glowing** outline/eyes), EmberKoi (volcanic: koi with **flame fins**, glowing), GoldenArowana (sunken ruins: gold armour, dragon whiskers)
- **Secret:** Megalodon (abyss: giant scarred shark), HydraEel (volcanic: **three-headed** eel, glowing eyes), SeaSerpent (sunken ruins: coiled serpent, finned crest)
- **Celestial:** StarfallWhaleShark (starfall lake: spots are **glowing stars**, galaxy skin)

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
