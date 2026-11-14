# Cannon Tame cannons (14 upgrade tiers, TFFA style)

Built by `tools/blender/cannons.py` (`/tmp/bpyenv/bin/python tools/blender/cannons.py [tiers] [--no-render] [--sheet]`) with the
TFFA kit in `.claude/skills/tffa-animal-models/`. Overview: `Cannons_overview.png`.

| # | Tier | Status | Look |
|---|---|---|---|
| 01 | Wooden | **done (style guide: base)** | studded: wood barrel with iron hoops on a stepped four-wheel carriage |
| 02 | Iron | **done** | studded field gun: dark iron barrel with brass rings on two big red spoked wheels, trail and ammo box |
| 03 | Stone | **done** | studded: stone idol-face barrel with moss on a roller sled |
| 04 | Bamboo | **done** | studded: lashed bamboo bundle launcher on a mat platform, leaves and coconuts |
| 05 | Copper | **done** | studded steam cannon: copper barrel with brass rings and a verdigris band, cog-gear wheels, back boiler with smokestack, pressure gauges and valve wheel |
| 06 | Candy | **done** | studded: pink candy-striped barrel with frosting drips, sprinkles and a cherry, chocolate-bar carriage, frosted donut wheels, lollipops |
| 07 | Golden | **done** | studded bridge tier: gold barrel with ruby/sapphire/emerald inlays, royal crown on the breech, gem-tipped crown muzzle, treasure-chest carriage on gold wheels, spilled coins |
| 08 | Frost | **done** | faceted: ice barrel with snow caps, frost bands and icicles, ice-shard crown muzzle, snowflake emblems, crystal cluster on an ice block riding a sled |
| 09 | Lava | **done** | faceted: basalt barrel with magma seams and cracks on a mini volcano (lava rivers, crater, magma pool), spiked crater muzzle |
| 10 | Toxic | **done** | faceted: sludge launcher on tank treads, hazard stripes, glowing goo canister on the breech, leaking waste drums, dripping nozzle |
| 11 | Cyber | **done** | faceted: twin-rail railgun with glowing coils on three mech legs |
| 12 | Dragon | **done** | faceted: dragon-head barrel (zoo RedDragon head) with open jaws around a fireball bore, black/gold carriage |
| 13 | Galaxy | **done** | faceted: hovering planet with Saturn ring and moons, rocket-fin barrel, black-hole muzzle with accretion disc |
| 14 | Celestial | **done (style guide: final)** | faceted: hovering marble/gold plinth, angel wings, spiked crown muzzle, glowing bore, halo and rune ring |

Sizes grow with the tier: Wooden is about 5 x 2.5 x 3 studs (L x W x H); Celestial about 7 x 5 x 5.6.

## Files per cannon
`<Name>.glb` (import this with the Roblox 3D Importer: 1 unit = 1 stud, fires toward -Z, pivot at the ground centre), `.fbx`, `.blend`,
`<Name>_Texture.png`, `<Name>_Detail.png`, `anims/<Name>_Idle.fbx` + `_Fire.fbx`, `previews/` (hero, side, front, back and the `anim` strip).

## Rig
One skinned mesh, plus a `<Name>_Glow` mesh on glowing tiers (set Material = Neon and Color to the glow colour below).
- `Body`: carriage or pedestal
- `Barrel`: pivots on the trunnion axle. Rotate this bone to aim (pitch and yaw)
- `Muzzle`: empty bone at the mouth of the bore, child of `Barrel`. Spawn food projectiles at `Muzzle.WorldPosition`
- Extras: `Wing_L/R`, `Halo` (spins around the barrel), `Ring` (ground rune ring, child of Root so it stays put while the plinth hovers)

Clips: `Idle` (loop: barrel sway, hover, halo and ring spin, wing breathing) and `Fire` (one-shot, 30 f: the barrel kicks up about 7° and slides back, then settles).

## Glow colours
| Cannon | Glow parts | Colour |
|---|---|---|
| FrostCannon | bore, seams, snowflakes, back snowflake, two crystals, two icicles | `#50D2FF` (80, 210, 255) |
| LavaCannon | crater magma, lava rivers, pool, seams, cracks, vents, bore, embers | `#FF5400` (255, 84, 0) |
| ToxicCannon | canister, bore sludge, drips, seams, turret ring, drum goo, puddle | `#46FF28` (70, 255, 40) |
| CyberCannon | rail strips, coils, charge ball, screens, knee and hub lights | `#FF3CB4` (255, 60, 180) |
| DragonCannon | fireball, mouth and eye glow | `#FF5C0C` (255, 92, 12) |
| GalaxyCannon | stars, core, accretion disc, ring glow | `#D678FF` (214, 120, 255) |
| CelestialCannon | bore, back core gem, halo, gem studs, ground rune ring | `#6EE1FF` (110, 225, 255) |
