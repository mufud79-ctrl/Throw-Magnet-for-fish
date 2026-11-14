# Cannon Tame shops (lobby stalls, TFFA style)

Built by `tools/blender/shops.py` (`/tmp/bpyenv/bin/python tools/blender/shops.py [CannonShop SellShop] [--no-render]`) with the
TFFA kit in `.claude/skills/tffa-animal-models/`. Overview: `Shops_overview.png`.

| Shop | Size (W x D x H studs) | Look |
|---|---|---|
| CannonShop | 15 x 11.5 x 16 | Wooden stall with a red/white striped awning and a pixel-block "CANNONS" sign (lettered on both sides). A big cannon sits on the roof as a landmark. Inside: a red counter with cannonball panels and cannonball piles, back-wall shelves of six mini display cannons in tier colours, powder kegs, and lanterns on the front posts |
| SellShop | 13 x 9.5 x 15 | Green stall with a stone deck, a green/white awning, a "SELL" sign (both sides) and a giant spinning-ready $ coin on top with sparkles. Inside: a green counter with a $ coin emblem, a balance scale (coins vs a ruby), coin stacks, money bags with a $ and gold piles |

## Files per shop
`<Name>.glb` (import with the Roblox 3D Importer: 1 unit = 1 stud, the counter faces -Z, pivot at the ground centre), `.fbx`, `.blend`,
`<Name>_Texture.png`, `<Name>_Detail.png`, `previews/` (hero, front, side, back).

Static props: one mesh and no rig, plus a `<Name>_Glow` mesh (set Material = Neon and Color to the glow colour below).
Sized for an R15 avatar (about 5 studs tall): the counter top is at 3.7 studs and the deck is 0.6 studs high (the front step is 0.3).
For a ProximityPrompt, put an invisible anchored Part in front of the counter (about 1.5 studs in front of the counter's front face, centred).

## Glow colours
| Shop | Glow parts | Colour |
|---|---|---|
| CannonShop | two lanterns | `#FFCC64` (255, 204, 100) |
| SellShop | two lanterns, two sparkles by the coin | `#FFF0A0` (255, 240, 160) |
