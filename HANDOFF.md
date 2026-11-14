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

**All 50 fish are built, rigged and animated** (see `animations/README.md`: 6 shared clips plus 6 family clips; rig in `tools/blender/rig.py`, clips in `fishanim.py`, export with `export_anims.py`, check frames with `anim_preview.py`). Possible follow-ups if the user asks:
- Polish passes on individual fish (render a `front` view by passing `views=` in the spec; dramatic fish sell on their front silhouette).
- EmberKoi body reads thin; the HydraEel's second neck is hidden in the 3/4 view.
- Variants (Gold/Shiny/Giant) as texture or colour swaps.
- Testing the imports in Roblox Studio (not done yet: confirm scale, facing and that Glow meshes import as separate MeshParts).

## Baits
15 stylised bait props in `models/Baits/<Rarity>/<Name>/`, built by `tools/blender/baits.py` (`python baits.py [Name ...] [--no-render]`); overview: `models/Baits/Baits_overview.png`.
- **Common:** BreadCrumbs, Earthworm, CornKernels. **Uncommon:** Cricket, Shrimp, SpinnerLure. **Rare:** SquidChunk, GlowWorm*, FrozenKrill. **Epic:** RawSteak, MagmaPepper*. **Legendary:** PhantomJelly*, RuneCookie*. **Mythic:** DragonPearl*. **Celestial:** StardustMorsel* (* = `_Glow` mesh).
- Props are static: `finish(rig=False)` skips the rig and clips (fish keep the default `rig=True`). `Bait` (in baits.py) adds generic builders on top of `Fish`: `ell` (deformable ellipsoid), `rbox` (rounded box), `slab` (extruded outline), `loft` (tube with surface lookup `at(s, angle)`), `strokes`; each part paints its own rectangle of the atlas body region. `done(scale, yaw)` sizes the item, turns long ones across the camera and frames the previews.
- All meshes are under 5k triangles. Weakest: CornKernels read more like jelly beans than kernels.

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

## Gym gear (dumbbell curls)
- 15 dumbbell tiers in `models/Gym/<NN>_<Theme>/<Theme>Dumbbell/` (Rusty → Rubber → Chrome → NeonSport → Golden → Crystal → Lava → Tiki → Cyber → Toxic → Kraken → Dragon → Galaxy → Angelic → Void), each cooler than the last. Built by `tools/blender/gym.py` (`python gym.py [tier numbers] [--bench-only] [--no-render]`).
- The game uses a **standing player doing alternating-arm curls**. The dumbbell origin is at the grip centre. An R15 curl animation was offered but not made.
- The preacher benches are **archived** in `models/Gym/_Archive_Benches/`, already resized to fit an R15 avatar. `tools/blender/fit_check.py` renders a bench with a blocky R15 stand-in.
- `gym.py` also provides the `Prop` class (adds `box`, `cyl`, `rock`, `cracks` and `project`, which box-projects the painted pattern onto a part) and `pat(kind, a, b)`, the painted patterns: rust, rubber, chrome, vinyl, gold, ice, obsidian, stone, carbon, hazard, scales, galaxy, marble, void, wood and ocean.

## UI (done)
- `ui/` holds the HUD buttons (Fish/equipped, Shop, Index), the Fish Index window, 50 thumbnails and silhouettes, icons and 9-slice frames.
- `ui/FishingUI.rbxmx` is the importable layout, with no scripts. `ui/asset_map.json` maps each PNG to the UI elements that use it.
- Scripts are in `tools/ui/`. Fish water areas are in `tools/ui/fishdata.py` (`AREA`) and match the 10 zones. After changing them, rebuild with `python3 tools/ui/build_rbxmx.py`.

## Zones: 10 zones, 6 unique props each (DONE, blocky underwater style)
Zones: 01_Pond, 02_River, 03_Swamp, 04_CoralReef, 05_OpenOcean, 06_FrozenSea, 07_DeepAbyss, 08_VolcanicVent, 09_SunkenRuins, 10_StarfallLake.
- **The game is visually underwater.** Props must make sense underwater (sunken versions, things seen from below, bubbles) and read through blue fog: bright, saturated colours, light tops, tall silhouettes and Neon accents.
- **The approved style for environment props is blocky Roblox-part builds**, in the vein of Grow a Garden, Steal an Egg and Throw Food for Animals:
  - Use `tools/blender/blocky.py` (`Brick` class): `block` (studs from `stud.png` on every face, 1 stud per cell), `wedge`, `cyl` and `ball` (smooth plastic), `rocks` (a cluster of rotated studded blocks), and `done(glow)`.
  - Minimal curves are fine: `seg()` in `zones_blocky.py` gives segmented cylinders with ball joints.
  - The user rejected both smooth sculpted props and faceted low-poly ones.
- `tools/blender/zones_blocky.py` builds all 60 props (`python zones_blocky.py [Zone or Prop names] [--no-render]`). No prop may repeat across zones.
- Possible polish: StatueHead and IcebergChunk are plain; FallenStar's glow arms read as a white smear in previews (Neon in Roblox).

## TFFA-style animals (skill) - CURRENT WORK
Develop on branch `claude/roblox-animal-models-852c5h`. Commit + push after every zone (another Claude session may push
to the same branch: `git fetch` + `git rebase origin/claude/roblox-animal-models-852c5h` before pushing; never rebuild a
zone that session owns). A second session works BOTTOM-UP (11_Space, 10_MythicIsles and 09_Volcano done; next 08_DinoLand,
then 07, 06...), skipping animals already rebuilt. Per-zone status + Roblox import notes: `models/CannonTame/Animals/README.md`.

**Skill:** `.claude/skills/tffa-animal-models/` - read `SKILL.md` first (workflow, look options table, kit cheat-sheet),
then `references/style_guide.md` and `references/review_checklist.md`. Reference models in `models/TFFA/`
(Gorilla, TRex, RedDragon, Phoenix, Cow; see `TFFA_vs_reference.png`).
**Roster:** `tools/blender/tffa_zoo.py` holds every Cannon Tame animal, building into `models/CannonTame/Animals/<Zone>/<Name>/`.
An entry is either a one-line archetype spec or `("<Name>", EX, "<script>")` = a hero build in
`.claude/skills/tffa-animal-models/examples/<script>.py` (zones 09-11, Chimera, Kraken, plus Gorilla/TRex/Cow/Phoenix).
Replaced versions are kept: models in `models/CannonTame/Animals/_Archive/<Name>_v<n>/`, scripts as `examples/_archive_<name>_v<n>.py`,
old specs as `# v1:` comments in the roster.

### Status (54 of 77 rebuilt in the new style, rigged with Idle/Walk[/Fly] clips; 23 left, all in zones 05-08)
| Zone | Done (new kit) | To do (still the old CannonTame look) |
|---|---|---|
| 01_Farm | all 7 | - |
| 02_Forest | all 7 | - |
| 03_Savanna | all 7 | - |
| 04_Jungle | all 7: Panther (snarl + muscular, user-approved), Crocodile, + hero scripts Frog (`dartfrog.py`: strawberry poison dart frog), Gorilla (`silverback.py`: roaring silverback), Monkey (`capuchin.py`: cheeky capuchin with banana), Sloth (`sloth.py`: moss + flower), Toucan (`toucan.py`: toco bill) | - |
| 05_Arctic | - | ArcticFox, Husky, Penguin, PolarBear, Seal, SnowOwl, Walrus |
| 06_Desert | Rattlesnake, Scorpion | Camel, FennecFox, Lizard, SphinxCat, Vulture |
| 07_IceAge | Mammoth (shaggy + fierce + muscular + studs, user-approved) | GiantBeaver, GiantSloth, Glyptodon, Sabertooth, WoollyHare, WoollyRhino |
| 08_DinoLand | Spinosaurus, Triceratops | Ankylosaurus, Compy, Parasaurolophus, Stegosaurus, TRex |
| 09_Volcano | all 7: EmberWolf, LavaRex, MagmaSlug, ObsidianGolem (hero scripts), FireSalamander (user-picked variation "Magma Newt"), LavaDrake (user-approved), Phoenix (reviewed example, rigged) | - |
| 10_MythicIsles | all 7: Chimera + Kraken (custom from user references), Pegasus/Unicorn (user-picked horse head H1, equine body), CelestialDragon (dragon archetype), Griffin, Jackalope | - |
| 11_Space | all 7 hero scripts; MoonBunny = user-picked "Saturn" variation, SpaceCat = user-picked "Alien" variation | - |

"Hard set" for future skill work (unusual anatomy, will need adjustments): Crocodile, Scorpion, Rattlesnake, Mammoth,
Triceratops, Spinosaurus, LavaDrake. Known weak spots: mammoth hair strands are flat blocks, scorpion tail segments are
plain, frill and sail are flat plates.

### User feedback to apply to the remaining animals
- **Quality bar = the custom Chimera** (`examples/chimera.py`, user: "THAT LOOKS SO GOOD!!"). Every animal in every
  remaining zone gets that level of detail: reference analysis first, a custom script per animal, 4-view review sheet,
  head studies when heads are weak. See `.claude/skills/tffa-animal-models/references/hero_build_workflow.md`.
- When a whole animal misses ("looks like a normal bunny", "looks rough"), build **4 full-body variations** with different
  concepts that change the silhouette (templates: `tools/blender/tffa_space_variants.py`, `tffa_salamander_variants.py`),
  show the sheet, let the user pick, refine, swap it in and archive the old one. Heads that miss: 4 head studies
  (`tools/blender/tffa_head_studies.py`; picks became the `lion_sunburst` / `horse_wedge` head kits).
- User verdicts so far: Chimera "THAT LOOKS SO GOOD!!"; Kraken "alright I guess, not the best"; the first SpaceCat,
  MoonBunny and FireSalamander were rejected (replaced by picked variations). Flames must show all three layers
  (red / orange / glowing yellow fanned apart - see `flame()` in `examples/emberwolf.py`); dark-skinned animals need white
  eyes with small pupils or glowing eyes, otherwise the eyes read as empty frames.
- Quality over speed: **one zone at a time**, review hero + front + side of every animal, fix, then commit.
- **Studs on everything** (the user rejected stud-less dragons and fur).
- Predators and big beasts must look **aggressive and muscular**: `snarl=True` (panther-style open jaw) for hunters such
  as the Sabertooth, EmberWolf and PolarBear; `fierce=True` for big herbivores (WoollyRhino, GiantSloth...);
  `muscular=True` on both. Rejected looks: "basic house cat", "dog with wings", "starved", "stubby", "elephant through chemo".
- Dragons (GalaxyDragon, CelestialDragon) must use the `dragon` archetype (`studded=True, muscular=True`), not `quad` + wings.
- The rattlesnake's coiled build was preferred over a redesign: when an animal already looks good, don't replace it.
- Keep every model animatable (rig + Idle/Walk, plus Fly for wings, exported automatically by `done()`), but **skip the
  animation previews for now** (`TFFA_ANIM_PREVIEW=0`).

### Paste-ready prompt for the next session
> Continue the TFFA-style rebuild of the Cannon Tame animals on branch `claude/roblox-animal-models-852c5h`.
> Read `HANDOFF.md` ("TFFA-style animals" section), `.claude/skills/tffa-animal-models/SKILL.md` and
> `.claude/skills/tffa-animal-models/references/hero_build_workflow.md` first; use the `tffa-animal-models` skill.
> Set up Blender with `python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy numpy`.
> 23 animals are left, all still in the old look: 05_Arctic (all 7), 06_Desert (Camel, FennecFox, Lizard, SphinxCat, Vulture), 07_IceAge (GiantBeaver, GiantSloth,
> Glyptodon, Sabertooth, WoollyHare, WoollyRhino) and 08_DinoLand (Ankylosaurus, Compy, Parasaurolophus, Stegosaurus, TRex).
> Another session may be working bottom-up on the same branch: before each zone, `git fetch` and skip any animal that
> already has an `anims/` folder. Do ONE zone at a time at the custom-Chimera quality bar (studs everywhere, aggressive +
> muscular predators, `TFFA_ANIM_PREVIEW=0`), review hero/front/side of every animal harshly, fix, rebuild, then commit and
> push (fetch + rebase first). Show me each zone's overview sheet.

## Cannons (Cannon Tame, 14 tiers) - IN PROGRESS
- `tools/blender/cannons.py` builds into `models/CannonTame/Cannons/<NN>_<Theme>/<Theme>Cannon/` (`python cannons.py [tiers] [--no-render] [--sheet]`); that folder's `README.md` has the roster, rig and glow table.
- Done: 01 Wooden, 02 Iron, 03 Stone, 04 Bamboo, 11 Cyber, 12 Dragon, 13 Galaxy, 14 Celestial. Remaining, built in pairs from both ends: 05 Copper + 10 Toxic, 06 Candy + 09 Lava, 07 Golden + 08 Frost.
- Early tiers use the studded look, late tiers the faceted look with one Neon glow colour. Every cannon is rigged (`Body`, a `Barrel` aim bone at the trunnion, an empty `Muzzle` bone for spawning projectiles) with `Idle` and `Fire` clips.
- Dragon: the user rejected heads built from boxes, so it reuses the zoo RedDragon head (`examples/dragon.py`) inside a frame. Their reference is `12_Dragon/DragonCannon_reference.webp`. Review harshly against references using a matching lens (about 90 mm telephoto for AI images).
