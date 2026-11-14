# Cannon Tame lobby props (TFFA style)

Built by `tools/blender/lobby.py` (`/tmp/bpyenv/bin/python tools/blender/lobby.py [LeaderboardGold LeaderboardPurple LeaderboardTeal Ranch] [--no-render]`),
sharing the helpers and static export in `tools/blender/shops.py`. Overview: `Lobby_overview.png`.

All props are static (no rig): import the `.glb` with the Roblox 3D Importer (1 unit = 1 stud, the front faces -Z, pivot at the ground centre).
Each comes as several MeshParts: the main mesh, extra named parts (below), and `<Name>_Glow` (set Material = Neon and Color to the glow colour).

## Leaderboards (one design, three colourways)
12 x 3.8 x 13.6 studs: a stone plinth, two pillars with orbs, a studded frame with a marquee of glowing bulbs, gold/silver/bronze medals beside
rows 1-3 on the left, and a header crest with stars and a gold trophy.

| Model | Frame | Accent | Screen | Glow |
|---|---|---|---|---|
| LeaderboardGold | gold | royal blue | navy | `#FFE282` (255, 226, 130) |
| LeaderboardPurple | violet | pink | deep purple | `#FF96F0` (255, 150, 240) |
| LeaderboardTeal | teal | orange | dark teal | `#8CFFE2` (140, 255, 226) |

`<Name>_Screen` is a flat 7.6 x 6.4 stud panel of its own: put a SurfaceGui on it (Face = Front, SizingMode = PixelsPerStud) for the rankings.
The header banner has no text, so the title (e.g. "Most Coins", "Most Tamed", "Top Cannons") can go in the SurfaceGui or a BillboardGui.

## Ranch
29.7 x 24.9 x 13.8 studs: a fenced pen (posts and two rails) on a grass rim with a dirt floor. The gate arch at the front has a "RANCH" sign
(lettered on both sides), a long-horn skull and two lanterns. Inside: a water trough, a hay feeder and hay bales.

| Part | Use |
|---|---|
| `Ranch` | fence, arch, sign, props |
| `Ranch_Floor` | grass rim + dirt floor (delete it if the map has its own ground) |
| `Ranch_GateL`, `Ranch_GateR` | the two gate doors, closed. Hinges are at the arch posts: set each door's pivot to its outer edge, then rotate or tween it to open |
| `Ranch_Glow` | lanterns, `#FFCC64` (255, 204, 100) |

The gate opening is 8.4 studs wide (an R15 avatar or a big animal fits); the fence is 4.3 studs high.
