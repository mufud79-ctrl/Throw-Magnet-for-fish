# Cannon Tame animals (TFFA style)

77 animals in 11 zones (7 per zone), rebuilt in the "Throw Food For Animals" look with the skill in
`.claude/skills/tffa-animal-models/`. **61 of 77 are done** (rigged + animated); the other 16 still have the old
CannonTame look and are listed below.

## Status by zone
| Zone | Rebuilt (new TFFA style, rigged) | Still old look |
|---|---|---|
| 01_Farm | Chicken, Cow, Duck, Goat, Horse, Pig, Sheep | - |
| 02_Forest | BrownBear, Fox, Hedgehog, Owl, Rabbit, Raccoon, Squirrel | - |
| 03_Savanna | Giraffe, Hyena, Meerkat, Ostrich, Rhino, Warthog, Zebra | - |
| 04_Jungle | Crocodile, Frog, Gorilla, Monkey, Panther, Sloth, Toucan | - |
| 05_Arctic | ArcticFox, Husky, Penguin, PolarBear, Seal, SnowOwl, Walrus | - |
| 06_Desert | Rattlesnake, Scorpion | Camel, FennecFox, Lizard, SphinxCat, Vulture |
| 07_IceAge | Mammoth | GiantBeaver, GiantSloth, Glyptodon, Sabertooth, WoollyHare, WoollyRhino |
| 08_DinoLand | Spinosaurus, Triceratops | Ankylosaurus, Compy, Parasaurolophus, Stegosaurus, TRex |
| 09_Volcano | EmberWolf, FireSalamander, LavaDrake, LavaRex, MagmaSlug, ObsidianGolem, Phoenix | - |
| 10_MythicIsles | CelestialDragon, Chimera, Griffin, Jackalope, Kraken, Pegasus, Unicorn | - |
| 11_Space | AlienBlob, AstroDog, BlackHoleBeast, GalaxyDragon, MoonBunny, SpaceCat, StarWhale | - |

A rebuilt animal has an `anims/` folder; an old one does not.

## Hero builds (one script per animal)
Zones 05 and 09-11, the 04_Jungle Frog/Gorilla/Monkey/Sloth/Toucan (and the Chimera/Kraken) are **hero builds**: a dedicated script with a written reference analysis in its
docstring, at `.claude/skills/tffa-animal-models/examples/<name>.py`. Highlights:

| Animal | Signature |
|---|---|
| Chimera | built from the user's painting: stalking crouch, swept-back mane, snarling lion with glowing eyes, goat head on top with huge ringed C-curved horns, scaled snake tail |
| Kraken | built from the user's octopus painting: leaning egg mantle, angry glowing eyes, 8 long curling tentacles with suckers |
| Pegasus / Unicorn | user-picked horse head (head study H1) on an equine body; feather wings / glowing gold horn |
| MoonBunny | user-picked variation "Saturn": galaxy bunny inside a banded planetary ring, orbit halo + tiny moon |
| SpaceCat | user-picked variation "Alien": third eye, antennae, glowing crystals, orbiting orbs |
| StarWhale | humpback head + constellations; GalaxyDragon = dragon archetype in nebula colours; BlackHoleBeast = void predator under a black-hole orb |
| EmberWolf | hellhound: molten ribs, fanned 3-tone flame mane, obsidian horns, glowing maw |
| FireSalamander | user-picked variation "Magma Newt": basalt skin with lava cracks, obsidian spikes, glowing eyes |
| Frog | strawberry poison dart frog: red with black spots, blue Z-folded legs with toe pads, bulging eye domes, orange throat sac |
| Gorilla | roaring silverback on the reviewed TFFA gorilla: open jaw with fangs, silver saddle, pecs, deltoids, knuckles |
| Monkey | cheeky capuchin: heart-shaped face, cocked brow + toothy grin, peeled banana, question-mark tail |
| Sloth | three-toed sloth: eye stripes, sleepy lids + smile, three huge hooked claws, moss on the back, pink flower |
| Toucan | toco toucan: giant orange bill with red ridge and black tip, blue eye ring, white bib, red under the tail |
| PolarBear | roaring attack posture (head below the hump), frosted ice-blue scruff tips, ice crystals on the back, claw scars |
| ArcticFox | sly stalking hunter: narrowed ice-blue eyes, half-grin with a fang, neck + cheek ruff, huge curled tail with a frost tip |
| Husky | lead sled dog: husky mask with widow's peak, ice-blue eyes, panting fangs + tongue, red harness with a gold D-ring |
| Penguin | stern emperor penguin: orange ear patches, yellow upper chest, long black/orange beak |
| SnowOwl | landing pose with the wings raised in a wide V, golden glare, black barring, feathered boots |
| Seal | harbour seal with a fish clamped in its mouth, dappled spots, whiskers, V of hind flippers |
| Walrus | bull walrus: huge tusks, bristly moustache, blubber folds, battle scars |
| LavaRex / MagmaSlug / ObsidianGolem | basalt-armoured T-Rex with magma drool / slug with an erupting volcano shell / golem with a caged crystal heart |

Other rebuilt animals come from one-line archetype specs in `tools/blender/tffa_zoo.py`.

## Files per animal
`<Zone>/<Name>/`:
- `<Name>.glb`: import this in Roblox Studio (3D Importer, 1 unit = 1 stud, faces -Z, pivot at the ground centre). It holds the skinned mesh, the armature and all clips.
- `<Name>.fbx`, `<Name>.blend`, `<Name>_Texture.png`, `<Name>_Detail.png` (stud shading + mutation mask).
- `<Name>_Glow` mesh inside the GLB/FBX where the animal has glowing parts: set its Material to **Neon** in Roblox.
- `anims/<Name>_<Clip>.fbx`: Idle, Walk (and Fly for winged animals). Animation Editor > Import > From FBX Animation > Loop > Publish. Bone names are shared per family, so one upload works for every animal with the same bones.
- `previews/`: hero, front, side (+ ref, review sheets for hero builds).

Each zone folder has `<Zone>_overview.png`; zones 09-11 also have `<Zone>_review.png` (4 views per animal).

## Archive and design studies
- `_Archive/<Name>_v<n>/`: earlier versions the user asked to replace (Chimera_v1, Kraken_v1, MoonBunny_v2, SpaceCat_v2, FireSalamander_v1). The matching old scripts are `examples/_archive_<name>_v<n>.py`.
- `models/TFFA/HeadStudies/`: 4 lion + 4 horse heads (user picked L2 lion, H1 horse; they became head kits in the skill).
- `models/TFFA/SpaceVariants/`, `models/TFFA/SalamanderVariants/`: the 4-variation sheets the MoonBunny, SpaceCat and FireSalamander were picked from.

## Rebuilding
```bash
python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy numpy          # once per container
TFFA_ANIM_PREVIEW=0 /tmp/bpyenv/bin/python tools/blender/tffa_zoo.py <Zone or Name ...> --sheet
```
