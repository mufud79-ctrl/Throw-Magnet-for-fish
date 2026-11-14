# Cannon Tame cannons (14 upgrade tiers, TFFA style)

Built by `tools/blender/cannons.py` (`/tmp/bpyenv/bin/python tools/blender/cannons.py [tiers] [--no-render] [--sheet]`) with the
TFFA kit in `.claude/skills/tffa-animal-models/`. Overview: `Cannons_overview.png`.

| # | Tier | Status | Look |
|---|---|---|---|
| 01 | Wooden | **done (style guide: base)** | studded: wood barrel with iron hoops on a stepped four-wheel carriage |
| 02 | Iron | planned | studded |
| 03 | Stone | planned | studded |
| 04 | Bamboo | planned | studded |
| 05 | Copper | planned | studded |
| 06 | Candy | planned | studded |
| 07 | Golden | planned | studded, bridge tier |
| 08 | Frost | planned | faceted + glow |
| 09 | Lava | planned | faceted + glow |
| 10 | Toxic | planned | faceted + glow |
| 11 | Cyber | planned | faceted + glow |
| 12 | Dragon | planned | faceted + glow |
| 13 | Galaxy | planned | faceted + glow |
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
| CelestialCannon | bore, back core gem, halo, gem studs, ground rune ring | `#6EE1FF` (110, 225, 255) |
