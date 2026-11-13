# Map plan: hub + zone canyon, underwater look

Build this **directly in Roblox Studio through the Roblox Studio MCP** (real instances, not a Lua generator).
UI must always be real ScreenGui/Frame/TextLabel instances built in Studio, never UI created only by scripts.

## Order of work
1. **Underwater look first** (before anything else).
2. Hub + canyon geometry.
3. Fish models in their zones with their animations looping.

## 1. Underwater look (purely visual, normal physics)
Do **not** use Roblox Terrain water. Fake it to match the blocky, bright style:
- `Lighting.Atmosphere`: Density ~0.35–0.45, Offset 0, Color teal (0,150,200), Decay deep blue (0,60,120), Glare 0, Haze ~2. This is the blue fade with distance.
- `ColorCorrectionEffect`: slight cyan tint (200,235,255), Saturation +0.15, Contrast +0.05. `BloomEffect` so Neon accents glow.
- Sky: no clouds, sun or stars (CelestialBodiesShown false, StarCount 0); the haze hides the rest.
- **Water surface overhead**: a huge flat part high above the map (~Y 140), light cyan, partly transparent, seen from below.
- **Light shafts**: tall thin Neon parts at ~0.85 transparency, slanting down from the surface and slowly swaying.
- **Bubbles**: small round Glass balls rising from vents and rocks in the zones, plus a few rising from the player's head now and then (the diving feel).
- **Drifting specks** (marine snow) around the camera; swaying kelp stalks built from blocky segments.
- Ground is a **sandy studded checkerboard** in place of the reference's grass. Walls are terraced studded rock with coral and kelp on top, in place of dirt with trees.

## 2. Layout (taken from the reference screenshots)
**Hub:** a large rectangular field (~260 × 170 studs) sunk in a pit. Terraced studded walls (~3 tiers, ~48 studs tall) on all sides; the only opening is in the front edge.
- **5 ranch plots** in a row along the back. Each is a fenced rectangle (chunky studded wood fence) with a gap in the front. Leave room for the largest size, because ranch upgrades enlarge the plot (more fish slots). Each plot has:
  - **Bait shop**: blue/white striped stall with a glowing cyan pad. Only its owner sees it.
  - **Dumbbell curl station** (in place of the reference's pull-up bar): glowing gate with a dashed white circle to stand in.
  - **Curl upgrade pad**: round yellow pad right in front of the station.
  - **Ranch upgrade sign** at the front fence gap: "10 > 12" slots and the price.
- **Front-left:** 3 leaderboards (Most Fish, Top Money, Luckiest Catch).
- **Front-right:** sell stall, red/white striped with a SELL sign and a dashed red circle pad (opens the Sell screen).
- **Front-centre:** the **throw strip**, an orange/yellow checker ledge with a glowing white edge. It locks the player in place, shows the power meter ("TAP TO THROW!") and plays the throw animation. The canyon floor sits lower than the hub, past the ledge.

**Zone canyon:** a long straight canyon from the throw strip, same width as the strip, with tall terraced walls. It holds 10 zones in order, divided by thin white lines across the floor, each with its own floor/wall colours and its 6 props from `models/Zones/`:
01 Pond, 02 River, 03 Swamp, 04 Coral Reef, 05 Open Ocean, 06 Frozen Sea, 07 Deep Abyss, 08 Volcanic Vent, 09 Sunken Ruins, 10 Starfall Lake.
How far the magnet flies (meter timing plus strength) decides which zone it lands in.

## 3. Fish
- Import each fish `.glb` from `models/<Rarity>/<Name>/` (rigged, same bone names on every fish).
- Fish swim in their own zone (`tools/ui/fishdata.py` `AREA`) with the Idle/Swim clips looping (see `animations/README.md` for which fish use which clip).
- Clips can be published from `animations/*.fbx`. They can also be played without uploading by setting `Bone.Transform` every frame with the same maths as `tools/blender/fishanim.py` `clip()` (rotation-only, 30 fps, `LENGTH` frames per loop).

## UI references (all real UI)
Welcome Back (offline earnings), My Animals (plot list with Pick Up/Sell, Equip Best), Shop (Featured eggs with odds, Packs, Gamepasses, Free Item, Gift), Egg Odds, Gift player picker, Animal Index by zone, Settings, Inventory hotbar, Sell Animals (backpack value, Sell All), the "You caught…" popup, and HUD (Index/Shop/Animals buttons, strength and cash counters).
