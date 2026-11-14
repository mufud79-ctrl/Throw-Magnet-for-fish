# Cannon Tame lobby props (TFFA style)

Built by `tools/blender/lobby.py` (`/tmp/bpyenv/bin/python tools/blender/lobby.py [LeaderboardGold LeaderboardPurple LeaderboardTeal Ranch] [--no-render]`),
sharing the helpers and static export in `tools/blender/shops.py`. Overview: `Lobby_overview.png`.

All props are static (no rig): import the `.glb` with the Roblox 3D Importer (1 unit = 1 stud, the front faces -Z, pivot at the ground centre).
Each comes as several MeshParts: the main mesh, extra named parts (below), and on the leaderboards `<Name>_Glow` (set Material = Neon and Color to the glow colour).

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
29 x 25 x 4.6 studs: an open fenced pen, nothing else (no arch, roof or floor). Wooden posts every ~3.5 studs with two rails,
and a gate in the middle of the front side between two chunkier gate posts.

| Part | Use |
|---|---|
| `Ranch` | fence posts, rails, gate posts |
| `Ranch_GateL`, `Ranch_GateR` | the two gate doors, closed. Hinges are at the gate posts: set each door's pivot to its outer edge, then rotate or tween it to open |

The gate opening is 8.4 studs wide (an R15 avatar or a big animal fits); the fence is 4.3 studs high.
